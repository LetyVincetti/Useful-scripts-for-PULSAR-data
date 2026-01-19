#example usage:
#python3 test_github_mii.py "B0329+54" "03h32m59.4096s" "54d34m43.329s" 53.0914  -7.9133 "/Users/letiziavincetti/Desktop/TCD/project1/general_synoptic/"
'''
#it needs 3 txt files:
-pulsar coordinates in the form PSR_NAME RA_hms DEC_dms (see pulsar_coord.txt)
-time arrays in form PSR_name ['utc format'] (see file time_arrays.txt)
-jones elements in file in form of results[mjd] = [i elements, one i for each subbands] (see code jones_mii.py)
'''
import os
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord, get_sun
from astropy import units as u
import astropy.units as u
import ast
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Plot tool to visualize pointing_jones solution from DreamBeam as function of altitude,azimuth, time\n",
        epilog=(   "Example: PSR B0329+54 from I-LOFAR station\n"
            "  python3 mii_plot.py B0319+54 "
        
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("psr", type=str, help="Pulsar name")
    parser.add_argument("ra", type=str, help="Right Ascension (e.g. 03h32m59.4s)")
    parser.add_argument("dec", type=str, help="Declination (e.g. 54d34m43.3s)")
    parser.add_argument("latitude", type=float, help="Observer site latitude in degrees")
    parser.add_argument("longitude", type=float, help="Observer site longitude in degrees")
    parser.add_argument("--elevation", type=float, default=0,
                        help="Observer site elevation in meters (default: 0)")
    parser.add_argument("dir", type=str, help="/Users/letiziavincetti/Desktop/TCD/project1/general_synoptic/")
    
    args = parser.parse_args()
    
    working_dir=args.dir
    os.chdir(working_dir)
    data = []

    with open('pulsar_coord.txt', 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                pulsar=parts[0]
                ra_str=parts[1]
                dec_str=parts[2]
                data.append((pulsar, ra_str, dec_str))

    for pulsar, ra, dec in data:
        print(f"{pulsar}: {ra} {dec}")

    pulsar_dic = {pulsar: (ra, dec) for pulsar, ra, dec in data}

    pulsarname = args.psr
    latitude = args.latitude
    longitude = args.longitude
    elevation = args.elevation

    if pulsarname in pulsar_dic:
        ra, dec = pulsar_dic[pulsarname]
        print(f"Pulsar {pulsarname} \n RA: {ra} \n Dec: {dec}")
    else:
        print("Pulsar not in the sample")

    time_utc=[]
    with open(f"time_arrays.txt", "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith(pulsarname):
                time_start = line.find("[") + 1
                time_end = line.find("]")
                list_string_time = "[" + line[time_start:time_end] + "]"
                #elements for the list as string transformed in LIST
                utc_times = ast.literal_eval(list_string_time)
                time_utc.extend(utc_times)

    #print(time_utc)
    
    time = Time(time_utc, format="isot", scale="utc")

    # Observer location
    location = EarthLocation(lon=longitude * u.deg, lat=latitude * u.deg, height=elevation * u.m)

    # Object coordinates
    obj_coord = SkyCoord(ra=ra, dec=dec)

    # Alt/Az frame
    altaz_frame = AltAz(obstime=time, location=location)
    obj_altaz = obj_coord.transform_to(altaz_frame)

    # Convert to degrees
    alt_deg = obj_altaz.alt.to(u.deg).value
    az_deg = obj_altaz.az.to(u.deg).value

    results = {}

    with open(f"pointing_5min_{pulsarname}.txt", "r") as file:
        for line in file:
            line = line.strip()
            #check for match line format
            if line.startswith("results[") and "] = [" in line:
                #extract MJD key
                key_start = line.find("[") + 1
                key_end = line.find("]")
                mjd = float(line[key_start:key_end])

                #extract list of mii
                list_start = line.find("[", key_end) + 1
                list_end = line.find("]", list_start)
                values_str = line[list_start:list_end]
                values = [float(v.strip()) for v in values_str.split(",")]
            
                #entry in the dictionary
                results[mjd] = values

    x,y=[],[]

    for key,v in results.items():
        x.append(key)
        y.append(v)

    subband_array = np.arange(12, 499, 64)
    for i, sb in enumerate(subband_array):
        freq_sb=100.+(sb*(100./512))-0.5*(100./512)

    x=np.array(x)
    y=np.array(y)

    fig, fig1 = plt.subplots(3,1, figsize=(5, 10))
    for i, sb in enumerate(subband_array):
        freq_sb=100.+(sb*(100./512))-0.5*(100./512)
        fig1[2].plot(x, 1./y[:, i], label=f'Subband {sb}, {freq_sb:.2f} MHz')
    
    fig1[2].set_ylabel(r'$a_{\mathrm{eff}}/a_{\mathrm{eff}}^{\max}$')
    fig1[2].legend(loc='best')

    fig1[0].plot(time.mjd, alt_deg)
    fig1[0].set_xlabel('time mjd')
    fig1[0].set_ylabel('altitude')

    fig1[1].plot(time.mjd, az_deg)
    fig1[1].set_ylabel('azimuth')

    fig1[0].legend(loc='upper left')
    fig1[0].set_title(f'{pulsarname}')
    plt.show()

if __name__ == "__main__":
    main()

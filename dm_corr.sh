#!/usr/bin/bash

#path = path to output dir from running mehdi step of the pipeline
#filename="<pulsar_name>_DMtimeseries.dm"

#print columns of file dm
while read mjd dm err toa; do
   echo "$mjd $dm $err $toa"
done < 'path/filename'

#array for dm column
dm_arr=()
while IFS=' ' read -r _ dm _ _; do
  dm_arr+=("$dm")
done < 'path/filename'

for each in "${dm_arr[@]}"
do
  echo "$each"
done

#change dm and dedisperse profile
files=(*.updated_eph)
n=${#files[@]}

for ((i=0; i<n; i++)); do
   dm_val="${dm_arr[$i]}" 
   file="${files[$i]}"
 
   pam -d $dm_val -m $file
   pam -D -m $file

done

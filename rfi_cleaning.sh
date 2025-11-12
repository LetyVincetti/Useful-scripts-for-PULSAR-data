#!/usr/bin/bash

for file in *.ar;
do
 
   base="${file%%_P000_f10s}"
   new="${base}.rficlean"
  echo  python /mnt/ucc4_data1/data/letizia/iterative_cleaner.py $file -c 5 -s 5 -m 3 -z -u -o $new --bad_subint 0.8 --bad_chan 0.8

done

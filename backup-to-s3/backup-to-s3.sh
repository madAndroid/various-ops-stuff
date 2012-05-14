#!/bin/bash

set -x
set -e

base_dir=$1
s_term=$2


file_list=`find $base_dir -name "*$s_term*"`
exclude_cmd="lsof +D $base_dir | awk \'{print $9}\' | grep $s_term" 

#echo $file_list
#echo $exclude_list

for file in $file_list
    do
        if [[ `lsof +D $base_dir | awk '{print $9}' | grep $s_term | grep $file` ]]; then
                echo "$file is open"
            else
                readyfiles="$readyfiles $file"
        fi
done

#echo $readyfiles

for file in $readyfiles
    do
        echo $file
done



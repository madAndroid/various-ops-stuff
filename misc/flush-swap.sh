#!/bin/bash -x

sudo sync
echo "Dropping caches"
sudo /sbin/sysctl vm.drop_caches=3
free -m
echo "Turning swap off"
sudo swapoff -a &
while [ $(free | grep -i swap | awk '{print $3}') -gt 0 ]; do
    sleep 2
    free -m
done
echo "Turning swap back on"
sudo swapon -a
free -m

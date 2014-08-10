#!/bin/bash

set -e

sudo sync
echo "Dropping caches"
sudo /sbin/sysctl vm.drop_caches=3
free -m
echo "Turning swap off"
sudo swapon -s
sudo swapoff -a &
while [ $(free | grep -i swap | awk '{print $3}') -gt 0 ]; do
    free -m | grep -i swap; printf "\033[A"
done
echo "Turning swap back on"
sudo swapon -s
sudo swapon -a
free -m

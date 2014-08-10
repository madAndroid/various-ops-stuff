#!/bin/bash

ssh $1@`aws ec2 describe-instances --instance-ids $2 --output text | grep PRIVATEIPADDRESSES | awk '{print $4}'`

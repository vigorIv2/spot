#!/bin/bash
for v in /dev/mmcblk1 /dev/sda  ; do 
	echo "Testing Volume $v"
	sudo hdparm -Tt $v
done	
for v in /tmp /mnt/vol1  ; do 
	echo "Testing Volume $v"
	dd if=/dev/zero of=$v/output conv=fdatasync bs=384k count=1k; rm -f $v/output
done	

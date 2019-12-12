#!/bin/bash

LINKS="$(ls /dev/v4l/by-id)"
RES=""
if [ $? -eq 0 ]; then
	for LINK in $LINKS
	do
        	INFOS="$(sudo udevadm info --query=all --name=/dev/v4l/by-id/$LINK | grep video-index0)"
		if [ $? -eq 0 ]
        	then
                	RES="$RES /dev/v4l/by-id/$LINK"
        	fi
	done
fi
echo "$RES"

#!/bin/bash

LINKS="$(ls /dev | grep video)"
RES=""
for LINK in $LINKS
do
	INFOS="$(sudo udevadm info --query=all --name=/dev/$LINK | grep ID_V4L_PRODUCT=mmal)"
	if [ $? -eq 0 ]
	then
		RES="/dev/$LINK"
		break
	fi
done 

echo "$RES"

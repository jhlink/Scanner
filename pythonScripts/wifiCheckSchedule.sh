#!/bin/bash

routergateway=`ip r | grep default | head -1 | cut -d ' ' -f 3`
#echo $routergateway
wifiCheck=`ping -q -w 1 -c 1 $routergateway > /dev/null && echo ok || echo error`

if [ $wifiCheck = "error" ]; then
	/etc/init.d/network reload
	echo "network reloaded"
else
	echo "network optimal"
fi



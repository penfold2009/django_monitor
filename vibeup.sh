#!/bin/sh

################################################
### To use this file add it to /etc/custom    ##
### in the vibe config add the global command ##
###   vibeup_cmd = /etc/custom/vibeup.sh      ##
### SNMP trap will then be send on any link   ##
### state change.                             ##
################################################




   SNMPSERVER="78.129.203.122"
   SNMPPORT="2162"
   COMMUNITY="public_testserver"
   MIB="linkUp.1"

   echo "### $(date) ### $@" >> /tmp/vibeup.log

   status=$1
   time=$(date +%r)
   mac=$3
   addr=$2
   hostname=$(awk -vFS="'" '/hostname/{print $2}'  /etc/config/system)
   #ipaddress=$(ip route get 8.8.8.8 | awk '{print $7}')
   ipaddress=$6
   name=$( vibe-stat san |awk -F"(" -vMAC=${mac:-"empty"} -vIP=${addr:-"empty"} \
                                                            '$0~MAC||$0~IP {print $1}')
   link_name="$(echo -e "${name}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
   message="${ipaddress:-'Unknown'}|${mac:-'Unknown'}|${link_name:-'Unknown'}|\
            ${addr:-'Unknown'}|${status:-'Unknown'}|${hostname:-'Unknown'}"
   command="snmptrap -v2c -c $COMMUNITY -m+all $SNMPSERVER:$SNMPPORT '' $MIB s s \"$message\""
   logger "$command"
   echo $command >> /tmp/vibeup.log
   eval $command 2> /dev/null
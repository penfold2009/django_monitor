#!/usr/bin/env python

### Django imports
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","monitor_project.settings")
import django
django.setup()
from monitor_app.models import *
import datetime

#import ezgmail  ### ensure token.json  token.pickle exist in the running dir
from time import *
from os import system, _exit, remove, environ
from pathlib import Path
import sys
import json
from datetime import timedelta 
import re
from monitor_packages.snmp_functions import *
from monitor_packages.functions import *
from django.contrib.auth.models import User                                                                      



"""
Serving multiple network interfaces
+++++++++++++++++++++++++++++++++++

Receive SNMP TRAP/INFORM messages with the following options:

* SNMPv1/SNMPv2c
* with SNMP community "public"
* over IPv4/UDP, listening at 127.0.0.1:162
  over IPv4/UDP, listening at 127.0.0.1:2162
* print received data on stdout

Either of the following Net-SNMP commands will send notifications to this
receiver:

| $ snmptrap -v2c -c public 127.0.0.1:162 123 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.5.0 s test
| $ snmpinform -v2c -c public 127.0.0.1:2162 123 1.3.6.1.6.3.1.1.5.1

"""

##### snmp imports  ###########################
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import ezgmail
from time import sleep, ctime

import sys

TESTMODE = True

## https://stackoverflow.com/questions/54882149/using-pysnmp-as-trap-receiver-with-own-vendor-mib
## http://snmplabs.com/pysnmp/examples/smi/manager/browsing-mib-tree.html#pdu-var-binds-to-mib-objects
from pysnmp.smi import builder, view, compiler, rfc1902

# Assemble MIB browser
mibBuilder = builder.MibBuilder()
mibViewController = view.MibViewController(mibBuilder)
compiler.addMibCompiler(mibBuilder, sources=['./mibs/VOIPEX-VIBE-MIB.txt', './mibs/IF-MIB.txt' ])

mibBuilder.loadModules('VOIPEX-VIBE-MIB')


if TESTMODE :

  SERVERIP = "127.0.0.1"
  email_dict = {
    "ARITARI" : [ "colin.penfound@aritari.com" ],
    "OPTAINIUM" :[ "colin.penfound@aritari.com", "fred.flintstone@mailinator.com" ]
    }

else:

  original_stdout = sys.stdout # Save a reference to the original standard output
  f = open('snmptrap_generic.log', 'w',1)  ## use a 1 line buffer so writes to disk straight away.
  sys.stdout = f # Change the standard output to the file we created.
  
  SERVERIP = "78.129.203.122"
  email_dict = {
  "ARITARI"   : [ "colin.penfound@aritari.com", "keith.balding@aritari.com" ],
  "OPTAINIUM" : [ "colin.penfound@aritari.com", "keith.balding@aritari.com", "peter.elsey@optainium.com" ]
  }





def sendemail(email_address, subject, message):

    for emailaddr in email_address:
       print ("## Sending email to %s" % emailaddr)
       try: ezgmail.send(emailaddr,subject,message)
       except Exception as err: print ("failed to send email - %s" % err)
       sleep(1)



# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Transport setup

# UDP over IPv4, first listening interface/port
config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((SERVERIP, 1162))
)

# UDP over IPv4, second listening interface/port
config.addTransport(
    snmpEngine,
    udp.domainName + (2,),
    udp.UdpTransport().openServerMode((SERVERIP, 2162))
)

# SNMPv1/2c setup

# SecurityName <-> CommunityName mapping
config.addV1System(snmpEngine, 'my-area', 'public_testserver')



##############################################################################
def updatedb(server_ip_address, linkname, status):

   print("Up dating server entrie.")   

   ## Get the server from the ip address
   getip = ServerIpAddress.objects.filter(ip = '78.129.231.64')
   if getip.count() == 0:
     print ("IP %s not found" % server_ip_address)
     return
   
   elif getip.count() > 1 :
     print ("IP %s found multiple entries." % server_ip_address)
     for ipobj in getip: print(ipobj.ip, ipobj.server.name)
     return

   else:
     serveripobj = getip.first()
     server = serveripobj.server
     
     ## Get the link. ##
     getlinkobj = server.serverlink_set.filter(name = linkname)
     
     if getlinkobj.count() == 0:
      print("Link '%s' not found." % linkname)
      return

     elif getlinkobj.count() > 0:
        print ("Link %s found multiple entries." % linkname)
        for linkobj in getlinkobj: print ( "%s %s" % (linkobj.name, linkobj.server.name) )
     
     else:
        link = getlinkobj.first()
        link.staus = status
        print ("Updating status of link %s to %s" % (link, status))
        link.save()
        return


######################################################################################
def process_parameters (snmpstring):
      
      parameters = "ipaddress|mac|name|addr|status|hostname".split('|')
      parameter_dict = dict(zip(parameters,snmpstring.split('|')))
      for key in parameter_dict.keys(): print ("%10s:%s" % (key,parameter_dict[key]))
    
      if ('status' in parameter_dict.keys()):
        status = parameter_dict['status']
 
        ## If link is up or down send email ##
        if status == "down" or status == "hs_done":
          parameter_dict['status'] = parameter_dict['status'].replace('hs_done','Up')

          message = ""
          for key in parameter_dict.keys():
            message = message + ("%10s : %s \n") % (key, parameter_dict[key])
          
          if ('hostname' in parameter_dict.keys()):
            subject = ("SNMP Alert for %s. Link: %s" % (parameter_dict['hostname'], parameter_dict['status']))
          else:
            subject = ("SNMP Alert.")

          if '139.99.4.41' in snmpstring:    
             sendemail(email_dict["OPTAINIUM"], subject, message)
          else : sendemail(email_dict["ARITARI"], subject, message)

      updatedb( parameter_dict['ipaddress'], parameter_dict['name'], status )


##############################################################################
#decorate cbFun function using a class ##
class cbdecorator:
  def __init__(self, func):  # On @ decoration: save original func
    self.calls = 0
    self.func = func
    self.email_list = email_dict

  def __call__(self, *args, **func_kwargs): # On later calls: run original func
    self.outstring = self.func(*args, **func_kwargs)
    self.calls += 1
    print ("---------------------------------------------------------")
    print('## Trap %s' % self.calls )
    print ("## SNMP Trap dectected: %s : %s" % (self.calls, ctime()))
    print('##  %s' % self.outstring )

    process_parameters (self.outstring)

###############################################################################





################################################################################
# This function is called when a trap is detected.
# Callback function for receiving notifications
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
# Decorated so it can be passed varianbles and the number of calls
# recorded, and I wanted to test out a decorator...
@cbdecorator
def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    #print('Notification from ContextEngineId "%s", ContextName "%s"' % (contextEngineId.prettyPrint(),
    #                                                                    contextName.prettyPrint()))
    # http://snmplabs.com/pysnmp/examples/smi/manager/browsing-mib-tree.html
    # Run var-binds through MIB resolver
    # You may want to catch and ignore resolution errors here
    varBinds = [rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolveWithMib(mibViewController) for x in varBinds]
    for name, val in varBinds:    
        if "SNMPv2-SMI::snmpV2" in name.prettyPrint():
          email_text = str(val)
 #  outstring = outstring + "\n" + ('%s = %s' % (name.prettyPrint(), val.prettyPrint()))    
    return email_text

##################################################################################



# Register SNMP Application at the SNMP engine
ntfrcv.NotificationReceiver(snmpEngine, cbFun)
snmpEngine.transportDispatcher.jobStarted(1)  # this job would never finish







if __name__ == "__main__" :
# Run I/O dispatcher which would receive queries and send confirmations
 
  try:
    snmpEngine.transportDispatcher.runDispatcher()
  except:
    snmpEngine.transportDispatcher.closeDispatcher()
    if  TESTMODE is False:
      sys.stdout = original_stdout # Reset the standard output to its original value
      f.close()
    raise

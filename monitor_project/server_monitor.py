import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","monitor_project.settings")
import django
django.setup()
from monitor_app.models import *
import datetime

import ezgmail  ### ensure token.json  token.pickle exist in the running dir
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


# managed1 = Server.objects.get(name="Managed_server1")



serverfile = 'servers-testmode-django.json'

if len(sys.argv) != 1:
  serverfile = sys.argv[1]

else: serverfile = 'servers-testmode-django.json'


current_count = 0

myfile  = Path(environ['PWD'] + '/' + serverfile)

if myfile.is_file():
  with open(myfile) as json_file: server_list = json.load(json_file)
else:
  print ("File not found %s" % myfile)
  server_list = [{"testmode":0, "logfile": "server_monitoring.log", "statusfile":"server_status.log"}]


config_list = []
config_list = [config for config in server_list if "testmode" in config]


if len(config_list) is not 0:
   config_list= config_list[0]
   logfile = config_list['logfile']
   testmode = bool(config_list['testmode'])
   statusfile =    config_list['statusfile']

else:
   logfile = 'server_monitoring.log'
   statusfile =  'server_status.log'
   testmode = False
   print ("Logfile not specified using default %s" % logfile)


print("Logfile is %s" % logfile)
print ("status file is %s" % statusfile)







if __name__ == '__main__':



	intialise_server_list(server_list)
	managed1 = Server.objects.get(name = "ManagedServer1")
	mangedip1 = managed1.serveripaddress_set.first().ip
	SNMPWalk('vibePeerName',mangedip1,managed1.snmp_community)
	SNMPWalk('vibeTunnelStatus',mangedip1,managed1.snmp_community)
	snmplinks = [(c,x.split('=')[1]) for x in  enumerate(SNMPWalk('vibePeerName',mangedip1,managed1.snmp_community),1) if 'vibePeerName' in x]

	colin = User.object().first()
	# aritari = Company(name="Aritari")
	# aritari.save()


	# managed_server1 = Server(name = "Managed_server1", online= "True", company = aritari, snmp_community = "voipex")
	# managed_server1.save()

	# ### In [20]: Server.objects.filter(name = 'Managed_server1').first()
	# ### In [4]: managed1 = Server.objects.get(name="Managed_server1")


	# Aeftel   = ServerLink(name = "Aeftel_07-20191222",  server = managed_server1)
	# Parsa    = ServerLink(name = "Parsa_01-20191028",   server = managed_server1)
	# Saramad  = ServerLink(name = "Saramad_01-20200511", server = managed_server1)
	# Integral = ServerLink(name = "ntegral_01-20200303", server = managed_server1)
	# Adopac   = ServerLink(name = "Adopac_04-202001302", server = managed_server1)
	# Comdata  = ServerLink(name = "Comdata_02-20200114", server = managed_server1)

	# Aeftel.save()
	# Parsa.save()
	# Saramad.save()
	# Integral.save()
	# Adopac.save()
	# Comdata.save()


	# manged1_ip1 = ServerIpAddress(  ip ="217.147.84.3" , ping_status = True, server = managed_server1)
	# manged1_ip2 = ServerIpAddress(  ip ="217.147.84.1" , ping_status = True, server = managed_server1)
	# manged1_ip3 = ServerIpAddress(  ip ="217.147.84.4" , ping_status = True, server = managed_server1)
	# manged1_ip4 = ServerIpAddress(  ip ="217.147.84.5" , ping_status = True, server = managed_server1)

	# manged1_ip1.save()
	# manged1_ip2.save()
	# manged1_ip3.save()
	# manged1_ip4.save()

	# managed_server2 = Server(name = "Managed_server2", online= "True", company = aritari, snmp_community = "voipex")
	# managed_server2.save()


	# Abaid_Amin_07   = ServerLink(name = "Abaid Amin_07",  server = managed_server2)
	# Calllync_01     = ServerLink(name = "Calllync_01",  server = managed_server2)
	# Comdata_02      = ServerLink(name = "Comdata_02",  server = managed_server2)
	# EuroAfro_01     = ServerLink(name = "EuroAfro_01",  server = managed_server2)
	# Prolinks_01     = ServerLink(name = "Prolinks_01",  server = managed_server2)


	# Abaid_Amin_07.save()


	# Calllync_01.save()
	# Comdata_02.save()
	# EuroAfro_01.save()
	# Prolinks_01.save()


	# manged2_ip1 = ServerIpAddress(  ip ="88.150.147.4" , ping_status = True, server = managed_server2)
	# manged2_ip2 = ServerIpAddress(  ip ="88.150.147.14" , ping_status = True, server = managed_server2)
	# manged2_ip3 = ServerIpAddress(  ip ="88.150.147.24" , ping_status = True, server = managed_server2)
	# manged2_ip4 = ServerIpAddress(  ip ="88.150.147.34" , ping_status = True, server = managed_server2)


	# manged1_ip1.save()
	# manged1_ip2.save()
	# manged1_ip3.save()
	# manged1_ip4.save()



################################################################################


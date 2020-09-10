#!/mnt/D64242DF4242C3C9/work/GIT_Repos/django_monitor/venv_dj_monitor/bin/python


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


# managed1 = Server.objects.get(name="Managed_server1")



##serverfile = 'servers-testmode-django.json'
serverfile = 'testserver-only-django.json'




if len(sys.argv) != 1:
  serverfile = sys.argv[1]

##else: serverfile = 'testserver-only-django.json'
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
	

from os import system
from monitor_app.models import *
import re
import ezgmail  ### ensure token.json  token.pickle exist in the running dir
from pathlib import Path
import json


def ping(server):

	for ipobj in server.serveripaddress_set.all():
		print ("pinging %s" % ipobj.ip)
		ping_rep = system('ping -qc 1 -w 2 ' +  ipobj.ip + '> /dev/null')

		if not ping_rep:
			ipobj.pingstatus = "Passed"
		else: ipobj.pingstatus = "Failed"
		ipobj.save()




def sendemail(server, subject, message):

    for emailaddr in server.email_list:
       logprint ("Sending email to %s" % emailaddr)
       try: ezgmail.send(emailaddr,subject,message)
       except Exception as err: logprint ("failed to send email - %s" % err)
       sleep(1)


# def intialise_server_list(server_list, serverfile):
# 
#   try: return [ Server(ipaddresslist = server['ipaddress'],
#                       community = server['community'],
#                            name = server['name'],
#                           email = server['emaillist'],
#                   parameterlist = checktest(server),                  
#                        testlist = server['testlist'] ) for server in server_list if "logfile" not in server ]
#   except Exception as err: 
#     logprint ("\n\nError reading json file %s" % serverfile)
#     logprint ("Error - %s" % err)


def setup_serverlist( serverfile = 'servers-aritari.json'):

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

	return server_list, logfile, statusfile,testmode




def add_server_to_db (server):
			print ("function: add_server_to_db") 
	# if Company.objects.all().filter(name = server['company']):
			if Company.objects.filter(name = server['company']):
				db_company = Company.objects.get(name = server['company'])
				print (db_company.name, " exists")
			else : 
				db_company = Company(name = server['company'])
				db_company.save()

			print ("#### Check Servers ### ")
			# if Server.objects.filter(name = server['name']):
			#if Server.objects.filter(name = server['name']):
			if Server.objects.filter(name = server['name']):
				if Server.objects.get(name = server['name']).company.name == server['company']:
					return ("Server '%s' already exists for %s" % (server['name'], server['company']))

			else:
				db_server = Server( name = server['name'], 
								online= "True", 
								snmp_community = server['community'], 
								email_list = server['emaillist']
			)

			db_server.save()
			#print(db_company.name)
			print("Adding %s to %s" % (db_server,db_company))
			db_company.server_set.add(db_server)
			db_company.save()

            ## ip addresses
			if 'ipaddress' not in server.keys():
				return ("Error no ip addresses specified")
				
			else :
				for ip in server['ipaddress']:
					ip = ServerIpAddress(ip=ip, server=db_server)
					ip.save()

			db_server.setuplinks(server)
			return (f"Set up links for {server['name']}")
			# for link in db_server.serverlink_set.all():
			# 	print ("Link is ", link)





def intialise_server_list():

	server_list, logfile, statusfile,testmode  = setup_serverlist()

	for server in server_list :
		if 'logfile' not in server:
			add_server_to_db (server)

			# # if Company.objects.all().filter(name = server['company']):
			# if Company.objects.get(name = server['company']):
			# 	db_company = Company.objects.get(name = server['company'])
			# 	print (db_company.name, " exists")
			# else : 
			# 	db_company = Company(name = server['company'])
			# 	db_company.save()

			# # if Server.objects.filter(name = server['name']):
			# if Server.objects.get(name = server['name']):
			# 	print ("Server '%s' already exists for %s" % (server['name'], server['company']))
			# else:
			# 	db_server = Server( name = server['name'], 
			# 		                online= "True", 
			# 		                snmp_community = server['community'], 
   #                                  email_list = server['emaillist']
			# 		        )

			# 	db_server.save()

			# 	#print(db_company.name)
			# 	print("Adding %s to %s" % (db_server,db_company))
			# 	db_company.server_set.add(db_server)
			# 	db_company.save()

	  #           ## ip addresses
			# 	if 'ipaddress' not in server.keys():
			# 		print ("Error no ip addresses specified")
			# 		continue

			# 	else :
			# 		for ip in server['ipaddress']:
			# 			ip = ServerIpAddress(ip=ip, server=db_server)
			# 			ip.save()

			# 	db_server.setuplinks(server)

			# 	# for link in db_server.serverlink_set.all():
			# 	# 	print ("Link is ", link)
					


def test_server_links(server):

  result_string = None
  subject = None

  for link in server.serverlink_set.all(): 
    for mib in link.mibparameter_set.all(): 
        result = mib.checkstat() 
        if result is not None: 
            if result_string is None:
               result_string = link.name + " : " + result
            else : result_string = result_string + "\n" + link.name + " : " + result 
  
  if result_string is not None:
     subject = "Change of state for links on %s" % server.name              
     result_string = "The following links change changed state on %s :" % (server.name) + "\n" + result_string
  
  return subject , result_string



def test_servers(company):
  for server in company.server_set.all():
    sub, mail = test_server_links(server)
    if mail is not None :
      print ("####",sub)
      print ("####",mail)



def test_companies():
	for company in Company.objects.all():
		test_servers(company)





### Note that snmp walk sends back duplicated of the links with different oids...
## eg two Knotelecom_01-20190226's come back and two Saramad_02-20191021.

def testalllinks (server, testname):

    for objip in server.serveripaddress_set.all():

     walklist = [ x for x in SNMPWalk(testname, objip.ip, server.snmp_community) if testname in x ]
     if (len(walklist) == 1) and "No SNMP response received" in walklist : print ('No response from ip %s' % objip.ip)

     else:
         for walkelement in walklist:
        #  print (walklist)
   #       print (pattern.match(walkelement).group(1,2))
   #       return [ pattern.match(walkelement).group(1,2) for walkelement in walklist]
           pattern = re.compile(r'.*' + testname + '\.([0-9]+) = (.+$)', re.UNICODE)
           oid, status  = pattern.match(walkelement).group(1,2)
           #print(pattern.match(walkelement).group(1,2))
           #print(oid, status)
           linkobj = ServerLink.objects.filter(server = server).filter(oid = oid).first()
           print(linkobj, oid ,status)
     return





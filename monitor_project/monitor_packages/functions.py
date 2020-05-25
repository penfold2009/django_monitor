from os import system
from monitor_app.models import *


def ping(server):

	for ipobj in server.serveripaddress_set.all():
		print ("pinging %s" % ipobj.ip)
		ping_rep = system('ping -qc 1 -w 2 ' +  ipobj.ip + '> /dev/null')

		if not ping_rep:
			ipobj.pingstatus = "Passed"
		else: ipobj.pingstatus = "Failed"
		ipobj.save()





# def intialise_server_list(server_list, serverfile):

#   try: return [ Server(ipaddresslist = server['ipaddress'],
#                       community = server['community'],
#                            name = server['name'],
#                           email = server['emaillist'],
#                   parameterlist = checktest(server),                  
#                        testlist = server['testlist'] ) for server in server_list if "logfile" not in server ]
#   except Exception as err: 
#     logprint ("\n\nError reading json file %s" % serverfile)
#     logprint ("Error - %s" % err)



def intialise_server_list(server_list):

	for server in server_list :
		if 'logfile' not in server:
			db_server = Server(name = server['name'], online= "True", snmp_community = server['community'])
			db_server.save()
			
			if Company.objects.all().filter(name = server['company']):
				db_company = Company.objects.all().get(name = server['company'])
				print (db_company.name, " exists")
			else : 
				db_company = Company(name = server['company'])
				db_company.save()

			print(db_company.name)
			print("Adding %s to %s" % (db_server,db_company))
			db_company.server_set.add(db_server)
			db_company.save()

            ## ip addresses
			if 'ipaddress' not in server.keys():
				print ("Error no ip addresses specified")
				continue

			else :
				for ip in server['ipaddress']:
					ip = ServerIpAddress(ip=ip, server=db_server)
					ip.save()

			db_server.setuplinks(server)

			for link in db_server.serverlink_set.all():
				print ("Link is ", link)
				


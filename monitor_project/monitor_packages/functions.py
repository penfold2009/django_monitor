from os import system


def ping(server):

	for ipobj in server.serveripaddress_set.all():
		print ("pinging %s" % ipobj.ip)
		ping_rep = system('ping -qc 1 -w 2 ' +  ipobj.ip + '> /dev/null')

		if not ping_rep:
			ipobj.pingstatus = "Passed"
		else: ipobj.pingstatus = "Failed"
		ipobj.save()



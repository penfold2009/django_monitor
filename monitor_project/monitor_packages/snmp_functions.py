
from pysnmp.hlapi import *

### Get an snmp parameter for a link. Try all ips in the server list.
### return as soon as parameter has been accessed.

def getparameter (server, parameter, oid):
  
   print ("ips are:", [ipobj.ip for ipobj in server.serveripaddress_set.all()] )
   for linkip in server.serveripaddress_set.all():

    print("getparamter try ip %s", linkip.ip)
    if linkip.pingstatus == "Passed":
        print ("SNMPGet(%s , %s , %s, %s)" % (parameter, linkip.ip, oid, server.snmp_community))
        try : stat = SNMPGet(parameter, linkip.ip, oid, server.snmp_community)
        except Exception as err: print ("Error - %s" % err)
        else:
          if "timeout" in str(stat):
            return ("Error: " + str(stat) )
          
          elif "No Such Instance currently exists" in str(stat):
            return  ("Error: " + stat[0].split(' = ')[1])


          elif len(stat) is not 0:
           return  stat[0].split(' = ')[1]
         
          else : return ("Error: Unknown" + str(stat))




def SNMPGet(myparam,IPAddress,OID,community):
  # SNMPGet ('vibeTunnelStatus', '78.129.231.65', 1, 'voipex')
  #if testmode == True: print ("SNMPGet %s %s %s %s" % (myparam,IPAddress,OID,community))
  result_list = []
  errorIndication, errorStatus, errorIndex, varBinds = next(

    getCmd(SnmpEngine(),
           CommunityData(community,mpModel=1),
           UdpTransportTarget((IPAddress, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('VOIPEX-VIBE-MIB', myparam, OID).addAsn1MibSource('file:///home/colin/.snmp/voipexmibs')),
            lookupNames=True, lookupValues=True)
  )

  if errorIndication:
     return errorIndication

  elif errorStatus:
     error_result = ('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
     return error_result
  else:
     for varBind in varBinds:
       # logprint(' = '.join([x.prettyPrint() for x in varBind]))
          resout = ' = '.join([x.prettyPrint() for x in varBind])
          result_list.append(resout)
  return result_list




def SNMPWalk(myparam,IPAddress,community):

  result_list = []
  result =  nextCmd(SnmpEngine(),
           CommunityData(community,mpModel=1),
           UdpTransportTarget((IPAddress, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('VOIPEX-VIBE-MIB', myparam).addAsn1MibSource('file:///home/colin/.snmp/voipexmibs')),
            lexicographicMode=True, 
            maxRows=5000,
            ignoreNonIncreasingOid=True,
            lookupNames=True,
            lookupValues=True
            )

  for errorIndication, errorStatus, errorIndex, varBinds in  result:
     if errorIndication:
       if str(type(errorIndication)) == "<class 'pysnmp.proto.errind.RequestTimedOut'>": 
        result_list.append(errorIndication.args)

       else : result_list.append(errorIndication)

     elif errorStatus:
       error_result = ('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
       result_list.append(error_result)
       logprint (error_result)    

     else:
       for varBind in varBinds:
          resout = ' = '.join([x.prettyPrint() for x in varBind])
          result_list.append(resout)

  return result_list


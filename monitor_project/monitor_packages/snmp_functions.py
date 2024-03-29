
from pysnmp.hlapi import *


## For debugging only  ### 

#from pysmi import debug
#debug.setLogger(debug.Debug('all'))

source_mibfiles="file:///home/monitor1/.pysnmp/mibs/source_mibs"
compiled_mibs="/home/monitor1/.pysnmp/mibs/compiled_mibs"
### Note: .pysnmp needs to be set to the correct group, eg www-data





### Get an snmp parameter for a link. Try all ips in the server list.
### return as soon as parameter has been accessed.

def getparameter (server, parameter, oid):
  
  for linkip in server.serveripaddress_set.all():
      return_val = False
      #print("getparamter try ip %s", linkip.ip)
      if linkip.pingstatus :
          print ("SNMPGet(%s , %s , %s, %s)" % (parameter, linkip.ip, oid, server.snmp_community))
          try : stat = SNMPGet(parameter, linkip.ip, oid, server.snmp_community)
          except Exception as err: print ("Error - %s" % err)
          else:
            if "timeout" in str(stat):
              return_val =  ("Error: " + str(stat) )
            
            elif "No Such Instance currently exists" in str(stat):
              return_val =   ("Error: " + stat[0].split(' = ')[1])


            elif len(stat) is not 0:
             return  stat[0].split(' = ')[1]
           
            else : return_val =  ("Error: Unknown" + str(stat))
   
  print ("No repsonse to ips returning False.")
  return return_val




def SNMPGet(myparam,IPAddress,OID,community):
  # SNMPGet ('vibeTunnelStatus', '78.129.231.65', 1, 'voipex')
  #if testmode == True: print ("SNMPGet %s %s %s %s" % (myparam,IPAddress,OID,community))
  result_list = []
  errorIndication, errorStatus, errorIndex, varBinds = next(

    getCmd(SnmpEngine(),
           CommunityData(community,mpModel=1),
           UdpTransportTarget((IPAddress, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('VOIPEX-VIBE-MIB', myparam, OID).addAsn1MibSource(source_mibfiles, destination=compiled_mibs)),
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
           ObjectType(ObjectIdentity('VOIPEX-VIBE-MIB', myparam).addAsn1MibSource(source_mibfiles, destination=compiled_mibs)),
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




#!/usr/bin/env python
## #!./venv_monitor/bin/python3.6

from os import system, _exit, remove, environ
environ.setdefault("DJANGO_SETTINGS_MODULE","monitor_project.settings")
import django
django.setup()
from monitor_app.models import *


from pysnmp.hlapi import *
import ezgmail  ### ensure token.json  token.pickle exist in the running dir
from time import *
from pathlib import Path
import sys
import json
from datetime import timedelta 
import re

### Note:  PySNMP will call PySMI automatically, parsed PySNMP MIB will ###
### be cached in $HOME/.pysnmp/mibs/ (default location).                ###
### so the mib files will be copied over to $HOME/.pysnmp/mibs/

##### time formatting ## 
# import time
# start_time = time.time()
# # your script
# elapsed_time = time.time() - start_time
# time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
# strftime("%H Hours %M minutes and %S seconds", gmtime(elapsed_time))

###########################################################################

if len(sys.argv) != 1:
  serverfile = sys.argv[1]

else: serverfile = 'servers-testmode.json'
#else: serverfile = 'servers-testmode.json'
#else: serverfile = 'servers-maxrtp.json'

current_count = 0

## create these as globals so that they can be used 
## by the function logprint which has already been defined.
## The alternative is to pass these vars to every logprint function call
## and every class/function that calls it.
#global logfile
#global testmode


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


############################################################################
class Logfile ():
   def __init__ (self, testmode, file):
      self.testmode = testmode
      self.file = logfile
      if testmode:
        print("Testmode. Writting to stdout.")

   def print(self,text):
         if self.testmode: print (text)
         else :
          with open(self.file,'a') as myfile: myfile.write(text + "\n")


############################################################################

logprint_obj = Logfile(testmode, logfile)
logprint = logprint_obj.print

       

########################################################################################

class Server():
  def __init__ (self, ipaddresslist, community, name, email , parameterlist, testlist ):
      self.name  = name
      self.community = community
      self.oid = 0
      self.email_list = email
      self.accessible = True      
      self.sendmail = False
     # self.pingstatus = "Passed"
      logprint ("\nInitializing server '%s'" % self.name)
      self.iplist = [ IPObject(ip) for ip in ipaddresslist]
      self.licensevalid = getparameter(self,"vibeLicenseValid",self.oid)
      self.licenseremain = getparameter(self,"vibeLicenseRemain",self.oid)
      self.licenseemailed = ''
      self.testlist =  {tests:val  for tests,val in testlist.items()}
      self.parameterlist = parameterlist
      self.setuplinks()

  def setuplinks(self):
     self.tunnelobjectlist = []
     for ipobj in self.iplist:
        logprint("trying ip %s" % ipobj.ip)
        parameter = "vibePeerIndex"
        try : mywalk = SNMPWalk(parameter,ipobj.ip,self.community)
        except: 
              logprint ("SNMPWalk ('%s','%s','%s')" % (parameter,ipobj.ip,self.community))
              logprint ("Error: Check that parameters are correct")

        else:
           if len(mywalk) == 1 and "No SNMP response" in mywalk[0][0]: 
            logprint ("No SNMP response from server at %s" % ipobj.ip)
            self.tunnelobjectlist=[]
            ping(self)
           else:
            ### get rid of list elements wihout 'vibePeerIndex' in them eg 'timeout messsages'
            tunnelidlist = [int(x.split(' = ')[1]) for x in mywalk if 'vibePeerIndex' in x]
            ##self.iplist.insert(0,self.iplist.pop(self.iplist.index(ipobj)))
            
            ### Create the list of tunnel objects ####
            self.tunnelobjectlist  = [Link(self, x) for x in tunnelidlist]
            self.accessible = True
            break

     if len (self.tunnelobjectlist) == 0:
        logprint ("Warning no links found for server %s" % self.name)
  
  def __repr__ (self):
       return str(self.name)



  def show_link_status (self,myfile):
      with open(myfile,'a') as myfile:
        myfile.write ("="*66+"\n")
        message = ("\nLink status for '%s' - %s\n" % (self.name, ctime()))
        myfile.write(message)
        myfile.write("-" * len(message)+"\n") 

        if self.tunnelobjectlist:
            for link in self.tunnelobjectlist:
              if 'TunnelStatus' in link.mibobjectlist.keys():
               thistunnelstatus = link.mibobjectlist['TunnelStatus'].mib_status or "Unkown"
               myfile.write  (" Link: %33s : oid: %d : %s\n"  % (link.tunnelname, link.oid, thistunnelstatus))
        
        else :  myfile.write  ("##  Warning failed to get links for %s ##\n" % self.name)



  def check_all_link_parameters(self):

    if len (self.tunnelobjectlist) != 0:
      self.resultslist = {}
      for tunnel in self.tunnelobjectlist:
        
        if tunnel.linkerror >= 2:
           logprint( "%s still in error. Rechecking links for server %s" % (tunnel.tunnelname, self.name) )
           self.setuplinks()
           return None

        else:
           self.resultslist[tunnel.tunnelname] = tunnel.checkallparameters()    
           if "Error" in self.resultslist[tunnel.tunnelname]: tunnel.linkerror += 1
           else :  tunnel.linkerror = 0

      if self.resultslist: return self.resultslist          
      else: return None
 
    else: logprint ("No links to test.")








####################################################################################################



class IPObject():
  def __init__(self,ip):
    self.ip = ip
    self.pingstatus = self.testping()

  def testping (self):
       ping_rep = system('ping -qc 1 -w 2 ' +  self.ip + '> /dev/null')
       if ping_rep:
        return ("Failed")
       else: return ("Passed")

  def __repr__ (self):
       return str(self.ip)
  
  def show_ping_status(self):
     return (self.ip, self.pingstatus)



########################################################

class Link ():

  def __init__ (self, parent_server, OID):
    self.server = parent_server
    self.oid = OID
    self.linkerror = 0
    self.tunnelname = getparameter(self.server,"vibePeerName" , self.oid)
    self.linkstatus  = "Uknown"

    testmode and logprint ("\n################## %s #####################" % self.tunnelname)
    self.mibobjectlist = {}
    for key,values in self.server.parameterlist.items():
         testmode and logprint ("\n\nLink: intializing '%s' %s" % (key,values))
         self.mibobjectlist[key] = MIBParameter(self, values)
    
  def checkallparameters(self):
#      checklist = [parameter.checkstat() for parameter in self.mibobjectlist]
      if self.mibobjectlist :
        checklist = [ self.mibobjectlist[name].checkstat() for name in self.mibobjectlist.keys()  ]

        testmode and logprint ("Link checklist: %s" % str(checklist))
        return [ x for x in checklist if x != None ]

      else : return ( "Error no Mibs for link %s on server %s " % (self.tunnelname, self.server.name))
  def __repr__ (self):
       return str(self.tunnelname)


#####################################################


##### These are the individual snmp parameters a link can have. #####
##### They are defined in the json file under parameterlist     #####
####  eg 
# "TunnelStatus"  :{ "name": "Link Status",
#                    "mib_parameter": "vibeTunnelStatus",
#                    "type" : "statechange",
#                    "email" : "yes"
#                  },
### In this case TunnelStatus will be the key in the Link object ##
### mibobjectlist dictionary file                                ##



class MIBParameter ():
  def __init__(self, link_obj, parameter_list):
    self.parent_link = link_obj
    self.transition_statetime = 0
    self.statetimestart = time()
    self.stateduration = 0
    self.name = None
    self.mib_parameter = None
    self.type = "statechange"
    self.email = "no"
    self.thresholdvalue = None
    self.correctthresholdvalue = None
    
    ## Get all paramters from json file. ##
    self.setuparameter(parameter_list)
    
    ## current_status = vaue from snmp
    ## mib_status = the stored value
    self.current_status = self.mib_status = None
    
    aspercentage = (lambda value,threshold: threshold/100 * value)
    
    
    if not self.name : self.name = self.mib_parameter
    
    if not self.mib_parameter :
       logprint("Error MIB parameter not set for mib %s" % self.parent_link.tunnelname)
    else :    
      self.current_status = self.mib_status = getparameter(self.parent_link.server,self.mib_parameter , self.parent_link.oid)
      testmode and logprint("'%s' is now set to '%s'"  % (self.name, self.mib_status))
    
    ### If a threshold vaue has been specified then check to see if it is given as a percentage or a value.
    ### If getting the max threshold value returns None then correctthresholdvalue is not treated as a percentage.
    if  self.thresholdvalue:   

      self.maxthresholdvalue = getthreshold(self.mib_parameter)
      
      if "%" in self.thresholdvalue and self.maxthresholdvalue: 
         self.correctthresholdvalue = int(aspercentage(int(self.thresholdvalue[:-1]), int(self.maxthresholdvalue)))
      
      elif "%" in self.thresholdvalue and not self.maxthresholdvalue:
         self.correctthresholdvalue = self.thresholdvalue[:-1]
         logprint("Warning: The value %s for %s will be treated as an absolute value, not a percentage" % (self.correctthresholdvalue, self.mib_parameter)  )
      
      else : self.correctthresholdvalue = self.thresholdvalue



    if self.correctthresholdvalue:
      if int(self.current_status)  >= int(self.correctthresholdvalue):
        self.mib_status = self.current_status = "above"
      else: self.mib_status = self.current_status = "below"

    testmode and logprint ("'%s' is now set to '%s'"  % (self.name, self.mib_status))

   # if testserver.tunnelobjectlist[1].mibobjectlist['TunnelStatus'].mib_status : 
   #   parent_link.linkstatus = testserver.tunnelobjectlist[1].mibobjectlist['TunnelStatus'].mib_status
    #### end of init ####

    
  def setuparameter (self, myparameter_list):
    for name,val in myparameter_list.items():
      #print ("Checking Parameter %s" % name)
      testmode and logprint ("Parameter %s set to %s" % (name , val))
      setattr(self, name,val)

   
  def checkstat(self):

       if not self.mib_parameter :
          logprint("Error MIB parameter not set for mib %s" % self.parent_link.tunnelname)
                 
       else:          
        return_string = ""
        self.current_status = getparameter(self.parent_link.server,self.mib_parameter , self.parent_link.oid)
        testmode and logprint("%s: %s : %s" % (self.parent_link.tunnelname, self.mib_parameter, self.current_status)  )
        if self.current_status and "Error" in self.current_status:
          logprint ("Error fetching param %s for link %s" % (self.mib_parameter, self.parent_link.tunnelname)   )
          self.current_status = "Error"
          #self.parent_link.linkerror += 1
          return_string = "Error"
        else: 
          
           ### 
           if self.correctthresholdvalue:
             if int(self.current_status)  >= int(self.correctthresholdvalue):
                self.current_status = "above"
             else: self.current_status = "below"


           if str(self.current_status) != str(self.mib_status):
              self.transition_statetime = time() - self.statetimestart
              logprint (" '%s' link '%s' for server '%s' has changed state to '%s' ." % (self.name, self.parent_link.tunnelname , self.parent_link.server.name, self.current_status) )

              if self.transition_statetime >= 180:
                 logprint (" '%s' link '%s' for server '%s' has changed state to '%s' for longer than 3 mins." % (self.name, self.parent_link.tunnelname , self.parent_link.server.name, self.current_status))
                 self.mib_status  = self.current_status
                 self.transition_statetime = 0
                 self.statetimestart = time()
                 
                 if self.email == "yes" :
                    if self.thresholdvalue:  return_string  = ("%s : %s threshold value of %s" % (self.name, self.mib_status, self.thresholdvalue) )
                    else : return_string  = ("%s : %s" % (self.name, self.mib_status) )
                 else : return_string = None

             
              else : return_string = None

           else :
                 self.transition_statetime = 0
                 self.statetimestart = time()
                 return_string = None

           self.parent_link.linkerror = 0

        return return_string

  def __repr__ (self):
       return str( ("%s" % (self.name) ) )



#################################################################
## Check the python converted mib file for the threshold value ##

def getthreshold(mibparamter):
  
  getline = False
  mibfile = (environ['HOME'] + '/.pysnmp/mibs/VOIPEX-VIBE-MIB.py')
  with open (mibfile) as myfile: 
      for line in myfile: 
          if (mibparamter +  ' = '  in line) : 
             getline = line
             break
                 
  if getline :
    pat  = re.compile('^(.+ValueRangeConstraint)\(([0-9]+, [0-9]+)\)(.+)$')                                                                                                            
    try : return pat.match(getline)[2].split(', ')[1]
    except : return None

  else: return None


#########################################################



### Get an snmp parameter for a link. Try all ips in the server list.
### return as soon as parameter has been accessed.

def getparameter (server, parameter, oid):
  
   for linkip in server.iplist:

    if linkip.pingstatus == "Passed":
        #if testmode == True : print ("SNMPGet(%s , %s , %s, %s)" % (parameter, linkip.ip, oid, server.community))
        try : stat = SNMPGet(parameter, linkip.ip, oid, server.community)
        except Exception as err: logprint ("Error - %s" % err)
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



def sendemail(server, subject, message):

    for emailaddr in server.email_list:
       logprint ("Sending email to %s" % emailaddr)
       try: ezgmail.send(emailaddr,subject,message)
       except Exception as err: logprint ("failed to send email - %s" % err)
       sleep(1)






def ping (server):

    pass_list = []
    failed_list = []
    message = ""
    subject = ""


    for ipobj in server.iplist:

        testmode and logprint ("pinging %s" % ipobj.ip)
        ping_rep = system('ping -qc 1 -w 2 ' +  ipobj.ip + '> /dev/null')
   
        if  ping_rep and ipobj.pingstatus == "Passed": 
            ipobj.pingstatus = "Failed"
            failed_list.append(ipobj.ip)
            subject = ("Server '%s' ping status.\n" % server.name)
            logprint ("%s Server %s:  %s failed to respond to ping." % (ctime(), server.name, ipobj.ip)   )

        elif not ping_rep and ipobj.pingstatus == "Failed":         
            ipobj.pingstatus = "Passed"
            pass_list.append(ipobj.ip)
            subject = ("Server '%s' ping status.\n" % server.name)
            logprint ("%s Server %s:  %s responded to ping." % (ctime(), server.name, ipobj.ip)   )

    testmode and print ("pass_list : %s" % pass_list)
    testmode and print ("failed_list : %s" % failed_list)

    if failed_list:
        message += ("\nThe following ips failed to respond to pings:\n %s" %  "\n " .join(failed_list))
    
    if pass_list:
        message += ("\nThe following ips responded to pings:\n %s" %  "\n ".join(pass_list))

    if 'Passed' in [iptest.pingstatus for iptest in server.iplist] : 
        testmode and logprint ("Server %s is accessible." % server.name)
        server.accessible = True
        message += ("\n\nServer '%s' is accessible on the following ips:\n " % server.name)
        message += ("\n ".join([x.ip for x in server.iplist if x.pingstatus == "Passed"]))
    
    else :  
        server.accessible = False
        testmode and logprint ("Server %s is not accessible." % server.name)
        message += ("\n\nServer '%s' is not accessible." % server.name)

    if testmode == True:
      logprint("-----------------------------------------")
      logprint ("Ping test returning subject and message.")
      logprint ("subject : %s " % subject)
      logprint ("message : %s" % message)
      logprint("-----------------------------------------")


    return (subject, message)




def SNMP(server):

    if hasattr(server,'tunnelobjectlist'):

      linklist = []
      nowtime = strftime("%H:%M:%S", gmtime(time()))

      testresults = server.check_all_link_parameters()

      testmode and  logprint("testresults" , testresults)
      if testresults :
       
        message = False
        subject = False

        for linkname in testresults:
          if testresults[linkname]:
            message = ("The folllowing parameters have changed on link '%s':\n\n" % linkname)
            for string in  testresults[linkname] : 
              message += (" %s \n" %  string  )

        if message: subject = ("%s: Change of link state \n" % server.name)
              
        return subject, message

      else : return False, False


      
      if linklist :
           subject = (" %s: Change of link state \n" % server.name)
           message = ("\n The following links have changed state: \n")
           for link in linklist :
               message += ("   Link '%s' has changed to %s\n" % (link.tunnelname,link.currentstate))
      
           return subject, message
      
      else: return False, False

    else :
       logprint ("Cant get details for server '%s'" % server) 
       return False, False




###################################################################################


def licensecheck (getserver):
  

  server = getserver
  sub = mess = False
  email = False

  testmode and logprint ("server.iplist: %s" % server.iplist)
  for linkip in server.iplist:

    if linkip.pingstatus == "Passed":

        licensestatus  = getparameter(server, "vibeLicenseValid",server.oid)
    
        if "Error" in licensestatus : ###  if its not the same day
            if testmode : print ("Error in licensestatus" )         
            sub = ("%s: Warning failed to get license status. .  " % server   )
            mess = ("Failed to get the license for server %s at ip %s.\n" % (server, linkip.ip))

        else:
            if str(licensestatus) != str(server.licensevalid) :
               
               if str(licensestatus) != 'valid' :
                  lictxt = "invalid"
               else: lictxt = "valid"          

               sub = ("Warning license for server %s '%s'.  " % (server, lictxt)   )
               mess = ("The license for server %s at ip %s is '%s'.\n" % (server, linkip.ip, lictxt))
               server.licensevalid = str(licensestatus)
               #email = True
           
            else:
              licremain = getparameter(server, "vibeLicenseRemain",server.oid)
              #strftime("%A - %d %B %y %H:%M:%S",     gmtime(time()+ int(licremain)))
              if testmode : logprint ("licremain :", licremain )         
              if server.licensevalid == "valid":
                  if int(licremain) <= 604080:  ## Less than one week in seconds.
                    sub = ("%s - License expiry warning. " % server.name)
                    mess = ("\nWarning license for %s is due to expire in %s" %  (server.name,str(timedelta(seconds = int(licremain)))))
                    mess += ("\nExpiry date: %s" % strftime("%A - %d %B %y %H:%M:%S",     gmtime(time()+ int(licremain))) )

        if testmode : print ("license emailed %s.  today is %s"  %(server.licenseemailed ,ctime().split(' ')[0] ))         
       

        if sub and (ctime().split(' ')[0] != server.licenseemailed): ###  if its not the same day
           if testmode : print ("License warning not emailed today" )         
           server.licenseemailed = ctime().split(' ')[0]
           return sub, mess
       
  else : return (False, False)



def runtests (server):
  if server.testlist:
    for function in server.testlist:

      if function ==  "ping" or server.accessible: ## if server is not accessible do the ping test only.
        if testmode == True : print("\n\n\n############ Test: %s - %s. ##################\n" % (function,server.name))      
        try:
           sub, mess = globals()[function](server)
           if testmode == True : print("Runtest -  function %s:\nsub : %s \nmess : %s" % (function,sub,mess))
           if bool(sub) and bool(mess) and server.testlist[function]['email'] ==  'yes':
             sendemail(server, sub, mess)

        except Exception as err: logprint ("Invalid function - %s" % err)
        if testmode == True : print("\n#########  End of Test : %s - %s. #################\n" % (function, server.name))      

  else: logprint("No test for server %s %s " % (server.name, server.testlist))



#### If there is no parameter list for a server in the json file then use the default link status. ###
def checktest(server):
    logprint ("Checking for parameterlist")
    defaultparameterlist = {'TunnelStatus' : { "name": "Link Status", "mib_parameter": "vibeTunnelStatus", "email" : "yes"} } 
    
    if 'parameterlist' in server.keys():
      return server['parameterlist']
    else: return  defaultparameterlist



def intialise_server_list(server_list, serverfile):

  try: return [ Server(ipaddresslist = server['ipaddress'],
                      community = server['community'],
                           name = server['name'],
                          email = server['emaillist'],
                  parameterlist = checktest(server),                  
                       testlist = server['testlist'] ) for server in server_list if "logfile" not in server ]
  except Exception as err: 
    logprint ("\n\nError reading json file %s" % serverfile)
    logprint ("Error - %s" % err)

############################################################################################


if __name__ == '__main__':


  if testmode == True:
    interval_count = 10
  else: interval_count = 60


  logprint ( "%s Starting script" % ctime() )
  logprint ( "Reading %s" % serverfile)

  server_objects =  intialise_server_list(server_list, serverfile)
  
  if not server_objects:
    logprint ("### Error initialising servers. Exiting.  ###")
    logprint ("### Check the log file for details.       ###")

    sys.exit(0)
  
  else:
    for server in server_objects: 
      server.show_link_status(logfile) 


  logprint ("\n #################### \n Checking Servers. \n")
  while True:

      try:
          
          if current_count >= interval_count:
             nowtime = strftime("%H:%M:%S", gmtime(time()))
             logprint ("\n##### %s - Reintialise Server list. #######\n" % nowtime, file=logfile)
             server_objects =  intialise_server_list(server_list, serverfile)
             for server in server_objects: server.show_link_status(statusfile) 
             current_count = 0

          else:
               current_count += 1
               if testmode : print ("current_count :", current_count )  
               for server in server_objects:
                 runtests(server)

          if testmode == True: sleep(30)
          else: sleep(60)

      except KeyboardInterrupt:
          logprint('Interrupted')
          try:
              sys.exit(0)
          except SystemExit:
              _exit(0)

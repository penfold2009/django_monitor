from django.db import models
from django.utils import timezone
from time import time
from monitor_packages.snmp_functions import *
from os import environ
import re
# Create your models here.
## https://stackoverflow.com/questions/9415616/adding-to-the-constructor-of-a-django-model



class Company(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.name


# IntegrityError: NOT NULL constraint failed:
# ValueError: Field 'id' expected a number but got 'None'.

class Server(models.Model):

    name = models.CharField(max_length=40, blank=True, null=True)
    snmp_community = models.CharField(max_length=40, blank=True, null=True)
    # ipaddresses = models.GenericIPAddressField(protocol='ipv4')
    #linknames = models.TextField()
    online = models.BooleanField(default=True)
    lastupdate = models.DateTimeField(default = timezone.now)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    teststring = ""

    def __str__(self):
        return self.name

    # def showtest(self):
    #     return self.teststring

    def setuplinks(self, server_parameters):
        parameter = "vibePeerIndex"
        for ipobj in self.serveripaddress_set.all():
         print ("checking ip %s" % ipobj.ip)
         try : mywalk = SNMPWalk(parameter,ipobj.ip.strip(),self.snmp_community)
         
         except: 
              print ("SNMPWalk ('%s','%s','%s')" % (parameter,ipobj.ip,self.community))
              print ("Error: Check that parameters are correct")
         else:
           if len(mywalk) == 1 and "No SNMP response" in mywalk[0][0]: 
            print ("No SNMP response from server at %s" % ipobj.ip)

           else : 
                  tunnelidlist = [int(x.split(' = ')[1]) for x in mywalk if 'vibePeerIndex' in x]
                  print (tunnelidlist)
                  for oid in tunnelidlist:
                     linkname = getparameter(self,"vibePeerName" , oid)
                     if "Error" in linkname:
                      print (linkname)
                     else: 
                        if ServerLink.objects.filter(name = linkname).first() :
                            linkobj = ServerLink.objects.filter(name = linkname).first()
                            try : getattr(linkobj, 'server')
                            except Exception as err: print ("Error. Cant get server for link %s ", (linkobj.name,err))
                            else: 
                              if linkobj.server == self:
                                 print ("link %s already exists for server %s" % (linkname, self))
                        else:
                          print ("Adding %s to %s" % (linkname, self)) 
                          linkobj = ServerLink( name = linkname, oid = oid, server = self)
                          linkobj.save()
                          linkobj.setuptests(server_parameters['parameterlist'], oid)




#########################################################

class ServerLink(models.Model):
    name = models.CharField(max_length=200,blank=True, null=True)
    status = models.CharField(max_length=20, default = "up")
    oid = models.IntegerField(blank=True, null=True)
    # ipaddresses = models.GenericIPAddressField(protocol='ipv4')
    server = models.ForeignKey(Server, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def setuptests (self, parameter_list, oid):
      miblist = []
      # print ('Parameters for link %s are %s' % (self, parameter_list))
      ### paramkey is the name of the test eg TunnelStatus ##
      for paramkey in parameter_list:
        print ("Setting up Parameter %s" % paramkey)
        subparam = parameter_list[paramkey]
        print ("mib subparameter %s"  % subparam)
        mib = MIBParameter( name = subparam['name'], 
              mib_parameter = subparam['mib_parameter'],
              thresholdvalue = 'thresholdvalue' in subparam.keys() and subparam['thresholdvalue'] or None,
              oid = oid,
              parent_link = self)
        mib.setupmib(subparam)
        miblist.append(mib)

      [mib.save() for mib in miblist]
     # mib_parameter_list = "parent_link name mib_parameter mibtype thresholdvalue correctthresholdvalue current_status mib_status".split()
     # MIBParameter.objects.bulk_update(miblist, mib_parameter_list)
     # MIBParameter.objects.bulk_create(miblist, mib_parameter_list)


class ServerIpAddress (models.Model):
    ip =  models.GenericIPAddressField(protocol='ipv4')
    pingstatus = models.CharField(max_length=20, default="Passed",blank=True, null=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE,  blank=True, null=True)



class MIBParameter (models.Model):

  parent_link = models.ForeignKey(ServerLink, on_delete=models.CASCADE, blank=True, null=True)
  #transition_statetime  = models.FloatField(blank=True, null=True)
  #statetimestart  = models.FloatField(default = time(),blank=True, null=True )
  #stateduration  = models.FloatField(blank=True, null=True)
  name = models.CharField(max_length=20,blank=True, null=True)
  mib_parameter = models.CharField(max_length=20,blank=True, null=True)
  mibtype = models.CharField(max_length=20, default="statechange",blank=True, null=True)
  thresholdvalue  = models.CharField(max_length=20, default = None,blank=True, null=True)
  correctthresholdvalue  = models.FloatField(blank=True, null=True)
  current_status = models.CharField(max_length=20, default = None,blank=True, null=True)
  mib_status = models.CharField(max_length=20, default = None,blank=True, null=True)
  oid = models.IntegerField(blank=True, null=True)

  ## Check the python converted mib file for the threshold value ##

  def getthreshold(self, mibparamter):
    
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



  def setupmib (self, subparam):
        aspercentage = (lambda value,threshold: threshold/100 * value)
        self.current_status = self.mib_status = None
        self.transition_statetime = 0
        self.statetimestart = time()
        self.stateduration = 0
        
        if not self.mib_parameter :
           logprint("Error MIB parameter not set for mib %s" % self.parent_link.tunnelname)
        else :    
          self.current_status = self.mib_status = getparameter(self.parent_link.server,self.mib_parameter , self.oid)
          print("'%s' is now set to '%s'"  % (self.name, self.mib_status))
        
        ### If a threshold vaue has been specified then check to see if it is given as a percentage or a value.
        ### If getting the max threshold value returns None then correctthresholdvalue is not treated as a percentage.
        if  self.thresholdvalue:   

          self.maxthresholdvalue = self.getthreshold(self.mib_parameter)
          
          if "%" in self.thresholdvalue and self.maxthresholdvalue: 
             self.correctthresholdvalue = int(aspercentage(int(self.thresholdvalue[:-1]), int(self.maxthresholdvalue)))
          
          elif "%" in self.thresholdvalue and not self.maxthresholdvalue:
             self.correctthresholdvalue = self.thresholdvalue[:-1]
             print("Warning: The value %s for %s will be treated as an absolute value, not a percentage" % (self.correctthresholdvalue, self.mib_parameter)  )
          
          else : self.correctthresholdvalue = self.thresholdvalue


          if self.correctthresholdvalue:
            if int(self.current_status)  >= int(self.correctthresholdvalue):
              self.mib_status = self.current_status = "above"
            else: self.mib_status = self.current_status = "below"
        



  #########################################################



  # def __init__(self, link_obj, parameter_list):
  #   self.parent_link = link_obj
  #   self.transition_statetime = 0
  #   self.statetimestart = time()
  #   self.stateduration = 0
  #   self.name = None
  #   self.mib_parameter = None
  #   self.type = "statechange"
  #   self.email = "no"
  #   self.thresholdvalue = None
  #   self.correctthresholdvalue = None


class Emails (models.Model):

      server = models.ForeignKey(Server, on_delete=models.CASCADE, blank=True, null=True)
      email = models.EmailField(max_length=20)

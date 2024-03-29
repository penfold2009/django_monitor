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

    def test_all_servers(self):
         for server in  self.server_set.all(): 
            server.test_all_links() 

        ## returns a dict view not just the values so need to cast as a list and get
        ## get the first element. See :  https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
        ## return  {self.name: {server.name:list(server.test_all_links().values())[0]  for server in self.server_set.all() } }



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
    email_list = models.TextField(blank=True, null=True)
    teststring = ""

    def __str__(self):
        return self.name

    # def showtest(self):
    #     return self.teststring

    def ip_list (self): ## Get alist of ips that can be dusplayed when mousing over the server name.
      return ' : '.join([ ipobj.ip for ipobj in ServerIpAddress.objects.filter(server_id = self.id) ])


    def setuplinks(self, server_parameters):
        parameter = "vibePeerIndex"
        for ipobj in self.serveripaddress_set.all():
         print ("checking ip %s" % ipobj.ip)
         try : mywalk = SNMPWalk(parameter,ipobj.ip.strip(),self.snmp_community)
         
         except Exception as err: 
              print ("SNMP Error %s",err)
              print ("SNMPWalk ('%s','%s','%s')" % (parameter,ipobj.ip,self.snmp_community))
              print ("Error: Check that parameters are correct")

         else:
           if len(mywalk) == 1 and "No SNMP response" in mywalk[0][0]: 
            print ("No SNMP response from server at %s" % ipobj.ip)
            ipobj.pingstatus = False
            ipobj.save()

           else : 
                  tunnelidlist = [int(x.split(' = ')[1]) for x in mywalk if 'vibePeerIndex' in x]
                  print (tunnelidlist)
                  for oid in tunnelidlist:
                     addlink = False
                     linkname = getparameter(self,"vibePeerName" , oid)
                     print ("linkname is '%s'." % linkname)
                     if not linkname:
                      print ("getparameter for link '%s' failed." % linkname)
                     else: 
                        linkobj = ServerLink.objects.filter(name = linkname).first()
                        if linkobj :
                            try : getattr(linkobj, 'server')
                            except Exception as err: print ("Error. Cant get server for link %s ", (linkobj.name,err))
                            else: 
                              if linkobj.server == self:
                                 print ("link %s already exists for server %s" % (linkname, self))
                              else: addlink = True
                        else:
                          addlink = True

                        if addlink:
                          print ("Adding %s to %s" % (linkname, self)) 
                          linkobj = ServerLink( name = linkname, oid = oid, server = self)
                          linkobj.save()
                          linkobj.setuptests(server_parameters['parameterlist'], oid)
      

      
    def test_all_links(self):
      for link in self.serverlink_set.all(): 
        #print ("Testing ", link.name)
        link.test_all_mibs()
      #return {self.name: { link.name :list(link.test_all_mibs().values())[0] for link in self.serverlink_set.all()}  }




#########################################################

class ServerLink(models.Model):
    name = models.CharField(max_length=200,blank=True, null=True)
    colour = models.CharField(max_length=200,blank=True, null=True, default="grey")
    status = models.CharField(max_length=20, default = "up")
    oid = models.IntegerField(blank=True, null=True)
    # ipaddresses = models.GenericIPAddressField(protocol='ipv4')
    server = models.ForeignKey(Server, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def setuptests (self, parameter_list, oid):
      miblist = []
      emailtest  = lambda checkemail: (checkemail == 'Yes' or checkemail  == 'yes' or checkemail == True) and True or False
      # print ('Parameters for link %s are %s' % (self, parameter_list))
      ### paramkey is the name of the test eg TunnelStatus ##
      for paramkey in parameter_list:
        print ("Setting up Parameter %s" % paramkey)
        subparam = parameter_list[paramkey]
        print ("mib subparameter %s"  % subparam)
        mib = MIBParameter ( name = subparam['name'], 
              mib_parameter = subparam['mib_parameter'],
              thresholdvalue = 'thresholdvalue' in subparam.keys() and subparam['thresholdvalue'] or None,
              oid = oid,
              parent_link = self,
              email = emailtest(subparam['email'])
              )

        mib.setupmib(subparam)
        miblist.append(mib)

      [mib.save() for mib in miblist]
     # mib_parameter_list = "parent_link name mib_parameter mibtype thresholdvalue correctthresholdvalue current_status mib_status".split()
     # MIBParameter.objects.bulk_update(miblist, mib_parameter_list)
     # MIBParameter.objects.bulk_create(miblist, mib_parameter_list)
    def test_all_mibs(self):
          for mib in self.mibparameter_set.all():
            mib.checkstat()

          #return {self.name: {mib.name :list(mib.checkstat().values())[0] for mib in self.mibparameter_set.all()} }



class ServerIpAddress (models.Model):
    ip =  models.GenericIPAddressField(protocol='ipv4')
    pingstatus = models.BooleanField(max_length=20, default=True,blank=True, null=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE,  blank=True, null=True)



class MIBParameter (models.Model):

  parent_link = models.ForeignKey(ServerLink, on_delete=models.CASCADE, blank=True, null=True)
  transition_statetime  = models.FloatField(blank=True, null=True)
  statetimestart  = models.FloatField(default = time(),blank=True, null=True )
  stateduration  = models.FloatField(blank=True, null=True)
  name = models.CharField(max_length=20,blank=True, null=True)
  mib_parameter = models.CharField(max_length=20,blank=True, null=True)
  mibtype = models.CharField(max_length=20, default="statechange",blank=True, null=True)
  thresholdvalue  = models.CharField(max_length=20, default = None,blank=True, null=True)
  correctthresholdvalue  = models.FloatField(blank=True, null=True)
  current_status = models.CharField(max_length=20, default = None,blank=True, null=True)
  mib_status = models.CharField(max_length=20, default = None,blank=True, null=True)
  oid = models.IntegerField(blank=True, null=True)
  email = models.BooleanField(max_length=20, default=True)

  ## Check the python converted mib file for the threshold value ##

  def getthreshold(self, mibparamter):
    
    getline = False
    # mibfile = (environ['HOME'] + '/.pysnmp/mibs/VOIPEX-VIBE-MIB.py')
    mibfile = compiled_mibs + '/VOIPEX-VIBE-MIB.py'


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



  def update_record(self):
    print (f"### Updating StateRecord for {self.name} to {self.current_status} for mib {self.name} ")

    db_mibrecord = StateRecord(
        mib_change = timezone.now(),
        mib_status = self.current_status,
        parent_mib = self
        )
    
    db_mibrecord.save()


  def setupmib (self, subparam):
        aspercentage = (lambda value,threshold: threshold/100 * value)
        self.current_status = self.mib_status = None
        self.transition_statetime = 0
        self.statetimestart = time()
        self.stateduration = 0
        setcolour = lambda state: state == 'up' and 'black' or 'grey'

        if not self.mib_parameter :
           print("Error MIB parameter not set for mib %s" % self.parent_link.name)
        else :    
          self.current_status = self.mib_status = getparameter(self.parent_link.server,self.mib_parameter , self.oid)
          print("'%s' is now set to '%s'"  % (self.name, self.mib_status))
          
          ###  set the tunnel status of the parent link. ## 
          if self.mib_parameter == "vibeTunnelStatus" :
            self.parent_link.status = self.mib_status
            self.parent_link.colour = setcolour(self.parent_link.status)
            print (" ## Setting %s to %s ## " % (self.parent_link.name, self.parent_link.status))
            self.parent_link.save()


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
        


  def checkstat(self):

       if not self.mib_parameter :
          print("Error MIB parameter not set for mib %s" % self.parent_link.name)
                 
       else:          
        return_string = ""
        self.current_status = getparameter(self.parent_link.server,self.mib_parameter , self.parent_link.oid)
        print("%s: %s : %s" % (self.parent_link.name, self.mib_parameter, self.current_status)  )
        if self.current_status and "Error" in self.current_status:
          print ("Error fetching param %s for link %s" % (self.mib_parameter, self.parent_link.name)   )
          self.current_status = "Error"
          #self.parent_link.linkerror += 1
          return_string = "Error"
        else: 
          
           ### 
           if self.correctthresholdvalue:
             if int(self.current_status)  >= int(self.correctthresholdvalue):
                self.current_status = "above"
             else: self.current_status = "below"


           if self.name == 'Link Status' and self.parent_link.status != self.current_status:
                self.parent_link.status = self.current_status
                if self.current_status == 'up':
                   self.parent_link.colour = 'black'
                else: self.parent_link.colour = 'grey'
                self.parent_link.save()


           if str(self.current_status) != str(self.mib_status):
              self.transition_statetime = time() - self.statetimestart
              print (" '%s' link '%s' for server '%s' has changed state to '%s' ." % (self.name, self.parent_link.name , self.parent_link.server.name, self.current_status) )

              self.update_record()

              if self.transition_statetime >= 180:
                 print (" '%s' link '%s' for server '%s' has changed state to '%s' for longer than 3 mins." % (self.name, self.parent_link.name , self.parent_link.server.name, self.current_status))
                 self.mib_status  = self.current_status
                 self.transition_statetime = 0
                 self.statetimestart = time()
                 
                 if self.email :
                    if self.thresholdvalue:  return_string  = ("%s : %s threshold value of %s" % (self.name, self.mib_status, self.thresholdvalue))
                    else : return_string  = ("%s : %s" % (self.name, self.mib_status))
                 else : return_string = None


              else : return_string = None

              print ("### Saving changes to db ###")
              self.save()

           else :
                 self.transition_statetime = 0
                 self.statetimestart = time()
                 return_string =None

           self.parent_link.linkerror = 0

        return return_string

  def __repr__ (self):
       return str( ("%s" % (self.name) ) )

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



class StateRecord (models.Model):

     parent_mib = models.ForeignKey(MIBParameter, on_delete=models.CASCADE, blank=True, null=True)
     mib_change = models.DateTimeField(default = timezone.now)
     mib_status = models.CharField(max_length=20, default = None,blank=True, null=True)

     @classmethod
     def stats(cls, get_name="all"):
        outlist = []
        if get_name == "all":
          stat_filter= cls.objects.all()
        else:
          stat_filter = cls.objects.filter(parent_mib__parent_link__name = get_name)

        for stat in stat_filter :
          server = stat.parent_mib.parent_link.server.name
          mib_name = stat.parent_mib.name
          link_name = stat.parent_mib.parent_link.name
          outlist.append([server, link_name, mib_name, stat.mib_status, stat.mib_change])
        return outlist


     def __repr__(self):
        return (f"{self.parent_mib.name}:{self.parent_mib.parent_link.name}:{self.parent_mib.parent_link.server.name}:{self.mib_status}")




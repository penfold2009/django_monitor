from django.shortcuts import render, get_object_or_404, redirect
from .models import Server, Company, ServerLink 
# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
import shelve
from monitor_packages.functions import *

from .forms import NameForm
from .forms import *

# https://www.edureka.co/community/73109/how-do-i-call-a-django-function-on-button-click

## https://docs.djangoproject.com/en/3.1/topics/forms/


def check_forms_are_valid(form_list):

  for Paramform in form_list:
    if not Paramform.is_valid():
      print (f"{Paramform.name} is not valid.")
      return False

  return True


def parameter_form(name, mib, use_threshold = False, postdata = None):

    form = Parameter_dynamic(data = postdata ,  param = name, mib = mib)
    form.name = name
    form.mib_parameter = mib
    form.use_threshold = use_threshold
    if not use_threshold:
      form.fields[f'{name}_threshold'].disabled = True
    return form


def get_name(request, form_data = None ,  report = None):


    if 'form_response' in request.path:

      print (f"request.path is {request.path}")
      print (f"form_data = {form_data}")

      print("################ request attributes ####################################")
      for attr in dir(request) :
        if not '_' in attr:
           print (f"request.{attr}  {getattr(request,attr)}")

        print ("Thanks very much")
        return render(request, 'serverapp/form_reply.html', {'name': form_data , 'report' : report})
  
    if request.method == 'POST':

        # if this is a POST request we need to process the form data
        print ("########################### request.POST.items ##########################")
        for key, val in request.POST.items():
               print (f"request.POST[{key}] = {val}")
          
        print ("POST request.POST.items")


        # create a form instance and populate it with data from the request:
        form = NameForm(data = request.POST)
        paramform_list = []
        paramform_list.append(parameter_form('TunnelStatus', 'vibeTunnelStatus', False, request.POST))
        paramform_list.append(parameter_form('Link Quality', 'vibeRemoteQuality', True, request.POST))


        # check whether it's valid:
        if form.is_valid() and check_forms_are_valid(paramform_list):
        #if form.is_valid():
            print ("Form is valid")

            # if this is a POST request we need to process the form data
            print ("########################### request.POST.items valid ##########################")
            for key, val in request.POST.items():
                   print (f"request.POST[{key}] = {val}")
              
#            print ("POST request.POST.items")


            print ("   Cleaned data : ")
            for key,data in form.cleaned_data.items():
              print (f"    {key} : {data}")

            print ("--------")
            print ("   Cleaned data for paramform_list : ")
            parameterdict = {}
            for paramform in paramform_list:

                  if paramform.cleaned_data.get(paramform.name + '_enable') :
                    print (f'{paramform.name} is enabled')
                    parameterdict[paramform.name] = {key.split('_')[1]:item for key,item in paramform.cleaned_data.items()}
                    parameterdict[paramform.name]['name'] = paramform.name
                    parameterdict[paramform.name]['mib_parameter'] = paramform.mib_parameter

            form.cleaned_data['parameterlist'] = parameterdict
            print (f"form.cleaned_data is now {form.cleaned_data}")
            server = form.cleaned_data['name']
            company = form.cleaned_data['company']
            print (f"ip address : {form.cleaned_data['ipaddress']}")
            # if Company.objects.filter(name = company):
            if   Company.objects.filter(name = company):
                if Company.objects.get(name = company).server_set.filter(name  = server):
                   error =  (f" {server} already exists for {company}" )
                   print (error)
                   return render(request, 'serverapp/form_test1.html', {'form': form, 'form_list' : paramform_list ,'error': error})
            
            report = add_server_to_db (form.cleaned_data)
            print (report)



            print ("--------------Redirecting ------")
            ## return HttpResponseRedirect('/thanks/')



            ### When redirecting to another view instead of an html tmeplate can use the 'reverse' function ##
            ### https://docs.djangoproject.com/en/3.1/intro/tutorial04/#write-a-minimal-form
            ### the url created will be something like :-
            ### http://127.0.0.1:8000/form_response/Aritari/Set%20up%20links%20for%20Office%20Rapid%20server2
            ### In urls.py this matches the url sting "path('form_response/<str:form_data>/<str:report>', views.get_name, name='get_name'),"
            ### and so will load the view get_name.
            ### notice there is another url for getname " path('form_test/', views.get_name, name='get_name'), "
            ### but the string format does not match so it will not be used.
            return HttpResponseRedirect(reverse('serverapp:get_name', args=(form.cleaned_data['company'], report)  ) )

    # if a GET (or any other method) we'll create a blank form
    else:



        print ("blank form")
        form = NameForm()

        paramform_list = []
        paramform_list.append(parameter_form('TunnelStatus', 'vibeTunnelStatus'))
        paramform_list.append(parameter_form('Link Quality', 'vibeRemoteQuality', True))


    return render(request, 'serverapp/form_test1.html', {'form': form, 'form_list' : paramform_list })






def confirm_request (request, name, action):

  print (f'name {name}')
  print (f'action {action}')
  print (request)

  template = 'serverapp/confirm_action.html'
  action2 = f'{action} {name}'
  context = {'action': action, 'name' : name}

  # if 'Delete' in action:
  #   print (f'Deleting {name}')
  #   server_obj = get_object_or_404(Server, name = name)
  #   server_obj.delete()

  return render(request, template, context)








def delete_server (request, number, server_name):
    server_obj = get_object_or_404(Server, name=server_name)
    server_obj.delete()

    context = {'companies': Company.objects.all(), 'varnumber': number}
    template = f'serverapp/base{number}.html'
    return render(request, template,context)


def test_links (request, number, server_name):
          server_obj = get_object_or_404(Server, name=server_name)
          server_obj.test_all_links()

          # test_server_links(server_obj)
          #Server.objects.get(name = server_name).test_all_links()
 ##         return HttpResponse(f"Updating links for {server_obj.name} path is {request.path}")

          context = {'companies': Company.objects.all(),
                      'action' : f'{server_name} Updated',
                    'varnumber': number}

          template = f'serverapp/base{number}.html'
          return render(request, template,context)
          # print (f"request.GET: {request.GET}")
          # next = request.GET.get('mybtn2')
          # print (f"## next: {next}")
          # return HttpResponseRedirect(next)


def serverlist(request):
    return HttpResponse("Hello, world. You're at the server list index.")

@login_required
def company_servertable(request, company_name):
    company_obj = get_object_or_404(Company, name=company_name)
    context = {'servers': company_obj.server_set.all(), 
           'company_name': company_name , 
           'company_obj':company_obj,
           'companies': Company.objects.all()
           }

    template = 'serverapp/servertable.html'
    return render(request, template, context)


@login_required
def company_servertablex(request, number, company_name):
    company_obj = get_object_or_404(Company, name=company_name)
    ipdict = {}
    for server in company_obj.server_set.all():
          ipdict[server.name] = []
          [ ipdict[server.name].append(ipobj.ip) for ipobj in server.serveripaddress_set.all()]

    context = {'servers': company_obj.server_set.all(), 
           'company_name': company_name , 
           'company_obj':company_obj,
           'companies': Company.objects.all(),
           'basenumber': number,
           'ipdictionary': ipdict
           }

    template = f'serverapp/servertable{number}.html'
    return  render(request, template, context)

    # return HttpResponse("You're looking at server %s." % company_obj.name)


# @login_required
# def base2(request):
#       # company_obj = Company.objects.filter(name=company_name).first()
#     #company_obj = Company.objects.get(name=company_name)
#     context = {'companies': Company.objects.all()}

#     template = 'serverapp/base2.html'
#     return render(request, template,context)

@login_required
def basex(request, number,  server = None, action=None):
      # company_obj = Company.objects.filter(name=company_name).first()
    #company_obj = Company.objects.get(name=company_name)
    print (f"action = {action}")
    print (f"server = {server}")


    if action == 'Delete':
      print (f'Deleting {server}')
      server_obj = get_object_or_404(Server, name = server)
      try : server_obj.delete(); action = 'Deleted'
      except : action = 'Delete Failed'

    context = {'companies': Company.objects.all(),
              'varnumber': number,
              'server' : server,
                'action' : action }

    template = f'serverapp/base{number}.html'
    return render(request, template,context)



########## Form bits #################################

@login_required
def new_entry_form(request,number):
  template=f'serverapp/form{number}.html'

  print ("### request.path : ",request.path)
 
  # for attr in dir(request) :
  #   if not '_' in attr:
  #     print (f"request.{attr}  {getattr(request,attr)}")

  return render(request, template)




def form_process (request):
  print ("Processing form")
  server_name = request.POST['server']
  community_string = request.POST['community']

  for key, val in request.POST.items():
       print (f"form_process:  {key} : {val}")

  #return HttpResponse(f"Response from form. server name is {server_name}\n community string is {community_string}")
#
  # return HttpResponseRedirect('/form_reply/', {'server':server_name})
  return HttpResponseRedirect(reverse('serverapp:form_reply', args=(server_name,)  ) )

  # return redirect(request, 'serverapp/form_reply.html' )

def form_reply (request, servername):

      for attr in dir(request):
         if attr != 'environ':
          print (f"{attr}: {getattr(request, attr)}")

 #     for key, val in request.POST.items():
 #      print (f"{key} : {val}")
      context = {'companies': Company.objects.all(),
                  'server' : servername}
      return render(request, 'serverapp/form_reply.html', context)


##############################################################################



## Not used   ###################################################
def company_old(request, company_id):

    linklist = []
    serverlist = []
    company  = Company.objects.get(pk=company_id)
    for server in company.server_set.all(): 
      print (server)
      serverlist = serverlist + [server.name] 
      for link in server.link_set.all(): 
          linklist = linklist + [link.name]
          print (link) 

      response = ('%s : Servers: %s links %s ' % (company, str(serverlist) , str(linklist)))

    return HttpResponse(response)
##    return HttpResponse("You're looking at company %s." % company)
####################################################################



## @login_required ###  https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
def all_details(request):
    print (' User is authenticated? %s '  % request.user.is_authenticated)
    
    attrlist = [attr for attr in dir(request) if not attr.startswith('_') and not '__' in attr and not 'environ' in attr]
    for attr in attrlist: 
      print ( '%s : %s' % (attr, getattr(request, attr)))
    
    ### This is basically what the @login_required decorator does.
    if request.user.is_authenticated :
   
       context = {'companies': Company.objects.all()}
       template = 'serverapp/all_details.html'
       return render(request, template, context)
      # return redirect ('/company_server/Optainium/')
    else :
      return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    





@login_required
def company_server(request, company_name):

    # company_obj = Company.objects.filter(name=company_name).first()
    #company_obj = Company.objects.get(name=company_name)
    print ('### Company name is %s' % company_name)
    company_obj = get_object_or_404(Company, name=company_name)
    context = {'servers': company_obj.server_set.all(), 
               'company_name': company_name , 
               'company_obj':company_obj,
               'companies': Company.objects.all()
               }

    template = 'serverapp/server_details.html'
    return render(request, template, context)


@login_required
def list_links(request, company_name, server_name):
    print ('### Server name is %s' % server_name)
    server_obj = get_object_or_404(Server, name=server_name)
    company_name = server_obj.company.name
    company_obj = get_object_or_404(Company, name=company_name)

    context = {'links': server_obj.serverlink_set.all(), 
               'company_name': company_name,
               'companies': Company.objects.all(),
               'company_obj' : company_obj,
               'server_name' : server_obj.name
              }

    template = 'serverapp/link_details.html'
    return render(request, template, context)


@login_required
def linkparameters (request, company_name, server_name, link_name):
      print ('### View is linkparameters')
      print ('### Link name is %s' % link_name)
      link_obj = Company.objects.get(name = company_name).server_set.get(name = server_name).serverlink_set.get(name = link_name)
      server_obj = get_object_or_404(Server, name=server_name)
      company_obj = get_object_or_404(Company, name=company_name)

      response = HttpResponse()
      response.write("You clicked on %s. : %d " % (link_obj, link_obj.oid))
      template = "serverapp/link_parameters.html"
      context = {'links': server_obj.serverlink_set.all(), 
               'company_name': company_name,
               'companies': Company.objects.all(),
               'company_obj' : company_obj,
               'server_name' : server_obj.name,
               'link_object' : link_obj
              }

      return render(request, template, context)

@login_required
def linkparameters3 (request, company_name, server_name, link_name):
      print ('### View is linkparameters2')
      print ('### Link name is %s' % link_name)
      print (f'### server name is {server_name}')
      print (f'### company name is {company_name}')
      link_obj = Company.objects.get(name = company_name).server_set.get(name = server_name).serverlink_set.get(name = link_name)
      server_obj = get_object_or_404(Server, name=server_name)
      company_obj = get_object_or_404(Company, name=company_name)

      response = HttpResponse()
      response.write("You clicked on %s. : %d " % (link_obj, link_obj.oid))
      template = "serverapp/parameter_table3.html"
      context = {'links': server_obj.serverlink_set.all(), 
               'company_name': company_name,
               'companies': Company.objects.all(),
               'company_obj' : company_obj,
               'server_name' : server_obj.name,
               'link_object' : link_obj,
               'servers': company_obj.server_set.all()
              }

      return render(request, template, context)



@login_required
def updatelinks (request, company_name, server_name):
  print ("## Function: updatelinks ")
  Server.objects.get(name = server_name).test_all_links()
  return HttpResponse("You clicked on update links %s  %s." % (company_name,server_name))



###https://docs.djangoproject.com/en/3.0/topics/auth/default/#how-to-log-a-user-in
def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        context = {'companies': Company.objects.all()}
        template = 'serverapp/base3.html'
        return render(request, template, context)

    else:
        # Return an 'invalid login' error message.
        return HttpResponse("Sorry invalid login.")

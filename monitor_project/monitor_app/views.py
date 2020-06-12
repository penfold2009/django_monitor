from django.shortcuts import render, get_object_or_404, redirect
from .models import Server, Company, ServerLink 
# Create your views here.
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
import shelve


def serverlist(request):
    return HttpResponse("Hello, world. You're at the server list index.")


def server(request, server_id):
    server = Server.objects.get(pk=server_id)
    links = server.link_set.all()


    return HttpResponse("You're looking at server %s." % server.name)

def company(request, company_id):

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
   ##    return redirect ('/company_server/Optainium/')
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



###https://docs.djangoproject.com/en/3.0/topics/auth/default/#how-to-log-a-user-in
def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        context = {'companies': Company.objects.all()}
        template = 'serverapp/all_details.html'
        return render(request, template, context)

    else:
        # Return an 'invalid login' error message.
        return HttpResponse("Sorry invalid login.")

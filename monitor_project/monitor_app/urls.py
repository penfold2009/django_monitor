from django.urls import path, re_path, include
from  . import views


app_name = 'serverapp'  ##https://docs.djangoproject.com/en/3.0/intro/tutorial03/#namespacing-url-names
                        
urlpatterns = [ ##path('', views.login_view, name='login_view'),
                path('', views.all_details, name='all_details'),
	            path('testpathfornoreason/', views.serverlist, name='viewname-serverlist'),
                path('company_server/<str:company_name>/', views.company_server, name='server'),
                re_path(r'^showlinks/(?P<company_name>.+)/(?P<server_name>.+)/$', views.list_links, name='links'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions
                re_path(r'^get_linkparams/(?P<company_name>.+)/(?P<server_name>[\w\s]+)/(?P<link_name>.+)/$', views.linkparameters, name='linkparameters'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions
                # path('get_linkparams/', views.linkparameters, name='linkparameters'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions

]


# urlpatterns_OLD = [ path('', views.serverlist, name='viewname-serverlist'),
# 	            path('testpathfornoreason/', views.serverlist, name='viewname-serverlist'),
# 	            # ex: /polls/5/
#                 path('server/<int:server_id>/', views.server, name='server'),
#                 path('company/<int:company_id>/', views.company, name='company'),
#                 path('links/<int:company_id>/', views.links, name='links'),
#                 path('all/', views.all_details, name='all_details'),
#                 path('company_server/<str:company_name>/', views.company_server, name='server'),
#                 re_path(r'^get_links/(?P<server_name>[\w\s]+)/$', views.links, name='links'),

# ]

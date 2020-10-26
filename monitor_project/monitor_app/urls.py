from django.urls import path, re_path, include
from  . import views


app_name = 'serverapp'  ##https://docs.djangoproject.com/en/3.0/intro/tutorial03/#namespacing-url-names
                        
urlpatterns = [ ##path('', views.login_view, name='login_view'),
                # path('', views.all_details, name='all_details'),
                path('', views.base , name='base' ),  ###https://docs.djangoproject.com/en/3.1/topics/http/urls/#passing-extra-options-to-view-functions
                path('company_server/<str:company_name>/', views.company_server, name='server'),
                path('company_servertable/<str:company_name>/', views.company_servertable, name='servertable'),
                path('update_links/<str:server_name>/', views.test_links, {'number' : 3}, name='test_links'),
                path('delete_server/<str:server_name>/', views.delete_server,{'number' : 3}, name='delete_server'),
                path('submitform/', views.form_process, name='form_process'),
                path('form_reply/<str:servername>', views.form_reply, name='form_reply'),
                path('form_newserver/', views.server_form, name='server_form'),
                path('form_response/<str:form_data>/<str:report>', views.server_form, name='server_form'),
                path('confirm/<str:name>/<str:action>', views.confirm_request_new, name='confirm_request_new'),
                path('confirm/<str:name>/', views.confirm_request_new, name='confirm_request_new'),

                re_path(r'^showlinks/(?P<company_name>.+)/(?P<server_name>.+)/$', views.list_links, name='links'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions
                re_path(r'^get_linkparams/(?P<company_name>.+)/(?P<server_name>[\w\s]+)/(?P<link_name>.+)/$', views.linkparameters, name='linkparameters'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions
                re_path(r'^base/(?P<server>.+)/(?P<action>.*)/$', views.base, name='base'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions
                path('get_linkparams/', views.linkparameters, name='linkparameters'), #https://docs.djangoproject.com/en/3.0/topics/http/urls/#using-regular-expressions
]


# urlpatterns_OLD = [ path('', views.serverlist, name='viewname-serverlist'),
#                re_path(r'^company_servertable(?P<number>[0-9]+)/(?P<company_name>.+)/$', views.company_servertablex, name='servertablex'),
#                  re_path(r'^new_entry_form(?P<number>[0-9]+)', views.new_entry_form, name='viewname-new_entry_form'),

# 	            path('testpathfornoreason/', views.serverlist, name='viewname-serverlist'),
# 	            # ex: /polls/5/
#                 path('server/<int:server_id>/', views.server, name='server'),
#                 path('company/<int:company_id>/', views.company, name='company'),
#                 path('links/<int:company_id>/', views.links, name='links'),
#                 path('all/', views.all_details, name='all_details'),
#                 path('company_server/<str:company_name>/', views.company_server, name='server'),
#                 re_path(r'^get_links/(?P<server_name>[\w\s]+)/$', views.links, name='links'),

# ]

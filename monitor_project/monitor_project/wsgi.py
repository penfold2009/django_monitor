"""
WSGI config for monitor_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os,sys

from django.core.wsgi import get_wsgi_application

#https://stackoverflow.com/questions/14927345/importerror-no-module-named-django-core-wsgi-apache-virtualenv-aws-wsgi
sys.path.append ('/home/colin/django_monitor/monitor_project')
sys.path.append('/home/colin/django_monitor/venv-dj-monitor/lib/python3.6/site-packages/')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_project.settings')

application = get_wsgi_application()

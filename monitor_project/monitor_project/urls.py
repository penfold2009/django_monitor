"""monitor_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

## https://stackoverflow.com/questions/9371378/warning-not-found-favicon-ico
from django.views.generic import RedirectView
from django.conf.urls import url

urlpatterns = [
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/serverapp/aritari-colorlogo.png')),
    path('', include('monitor_app.urls')),  ## 127.0.0.1:8000/serverapp
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),   ### for authenticating and logging in users.
]



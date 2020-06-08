from django.contrib import admin

# Register your models here.
## Models registered here are available at the admin login.

from .models import Company, Server, ServerLink

admin.site.register(Company)
admin.site.register(Server)
admin.site.register(ServerLink)


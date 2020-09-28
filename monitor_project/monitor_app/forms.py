from django import forms


class NameForm(forms.Form):
    company = forms.CharField(label='Company name', initial = 'Aritari',  max_length=100)
    name = forms.CharField(label='Server name',  initial = 'Office Rapid server',max_length=100)
    emaillist = forms.EmailField(label='email@address', initial = 'colin.penfound@aritari.com')
    ipaddress = forms.GenericIPAddressField(label='IP Adress', initial = '88.150.165.135')
    community = forms.CharField(label='SNMP Community',  initial = 'public',max_length=100)
    ping_test = forms.BooleanField(label='Ping Test', initial = True)
    SNMP_tests = forms.BooleanField(label='SNMP Tests', initial = True)
    license_check = forms.BooleanField(label='License Check', initial = True)

### Form created form server classss
### https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#modelforms-overriding-default-fields
from .models import Server
from django.forms import ModelForm

class NewServer(ModelForm):

     class Meta:

          server_name = forms.CharField(label='Server name', max_length=100)
          server_name = forms.CharField(label='Server name', max_length=100)



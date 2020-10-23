from django import forms

## http://www.learningaboutelectronics.com/Articles/How-to-add-a-class-or-id-attribute-to-a-Django-form-field.php
class NameForm(forms.Form):
    company = forms.CharField(label='Company name', initial = 'Aritari',  max_length=100,
               widget= forms.TextInput(attrs={'class':'form-control'})) ## Custom widgets with Bootstrap class properties.
 
    name = forms.CharField(label='Server name',  initial = 'Office Rapid server',max_length=100,
               widget= forms.TextInput(attrs={'class':'form-control'}))

    emaillist = forms.EmailField(label='email@address', initial = 'colin.penfound@aritari.com',
               help_text='A valid email address, please.',
               widget= forms.EmailInput(attrs={'class':'form-control'}))

    ipaddress = forms.CharField(label='IP Adress', initial = '88.150.165.135', max_length=200,
               widget= forms.TextInput(attrs={'class':'form-control'}))

    community = forms.CharField(label='SNMP Community',  initial = 'Rapidv1b3',max_length=100,
               widget= forms.TextInput(attrs={'class':'form-control'}))

    ping_test = forms.BooleanField(label='Ping Test', initial = True,required=False)
    license_check = forms.BooleanField(label='License Check', initial = True,required=False)
    SNMP_tests = forms.BooleanField(label='SNMP Tests', initial = True,required=False,
               widget= forms.CheckboxInput(attrs={ 'onclick': "showparameterform()", } ) )


## Dynamicly created form ##
## https://jacobian.org/2010/feb/28/dynamic-form-generation/
## Need to do this to dynamically define the 'name' of the inpout fields
class Parameter_dynamic (forms.Form):
    def __init__(self, *args, **kwargs):
        ## pull out the parameter names from the kwargs list
        param = kwargs.pop('param')
        mib = kwargs.pop('mib')

        ## Now initialise the main form class
        super(Parameter_dynamic,self).__init__(*args, **kwargs)
        self.fields[f'{param}_threshold'] = forms.IntegerField(label = 'Threshold Value', initial = 50)
        self.fields[f'{param}_enable'] = forms.BooleanField(label='Enable', initial = True, required = False)
        self.fields[f'{param}_email']  = forms.BooleanField(label='Email', initial = True,   required = False)
        # self.fields[f'{param}_mib']  = forms.CharField(label='', initial = mib, required = False,
        #                                                 widget = forms.HiddenInput() )














### Not used ###

class Quality (forms.Form):
        test = forms.CharField(label='Link Quality',  initial = 'Quality',max_length=100)
        parameter = forms.CharField(label='SNMP parameter',  initial = 'vibeRemoteQuality',max_length=100)
        email = forms.BooleanField(label='Email', initial = True)


## https://docs.djangoproject.com/en/3.1/ref/forms/widgets/
class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'special'})
        self.fields['comment'].widget.attrs.update(size='40')

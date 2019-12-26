from django import forms
from django.contrib.auth.forms import UserCreationForm
from bootstrap_modal_forms.forms import BSModalForm
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from .models import User, ContainerTemplate, UserDefaultTemplate


class CustomUserCreationForm(PopRequestMixin, CreateUpdateAjaxMixin,
                             UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

class ContainerTemplateModalForm(BSModalForm):

    dns_server_1 = forms.GenericIPAddressField(required=False)
    dns_server_2 = forms.GenericIPAddressField(required=False)

    class Meta:
        model = ContainerTemplate
        fields = ('friendly_name','image','shell', 'dns_server_1', 'dns_server_2', 'dns_search_domain', 'network_disable', 'user_id', 'working_dir', 'mount_volume', 'mount_location', )
        labels = {
            'network_disable': 'Disable networking?',
            'mount_volume': 'Mount user volume?',
            'working_dir': 'Working directory',
        }

class UserUpdateForm(BSModalForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)

class DefaultContainerTemplateForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user')
        super (DefaultContainerTemplateForm,self ).__init__(*args,**kwargs)
        self.fields['template'].queryset = ContainerTemplate.objects.filter(owner=user)

    class Meta:
        model = UserDefaultTemplate
        fields = {'template',}
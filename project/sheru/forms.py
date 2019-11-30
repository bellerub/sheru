from django import forms
from bootstrap_modal_forms.forms import BSModalForm
from .models import User, ContainerTemplate, UserDefaultTemplate

class ContainerTemplateModalForm(BSModalForm):
    class Meta:
        model = ContainerTemplate
        fields = ('image','shell',)

class UserUpdateForm(BSModalForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)

class ContainerTemplateForm(forms.ModelForm):
    class Meta:
        model = ContainerTemplate
        fields = ('image','shell',)

class DefaultContainerTemplateForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user')
        super (DefaultContainerTemplateForm,self ).__init__(*args,**kwargs)
        self.fields['template'].queryset = ContainerTemplate.objects.filter(owner=user)

    class Meta:
        model = UserDefaultTemplate
        fields = {'template',}
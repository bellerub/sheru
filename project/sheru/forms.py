from django import forms
from .models import User, ContainerTemplate, UserDefaultTemplate

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
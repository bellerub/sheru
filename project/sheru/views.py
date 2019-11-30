from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from .forms import DefaultContainerTemplateForm, ContainerTemplateForm, ContainerTemplateModalForm, UserUpdateForm
from .models import User, ContainerTemplate, UserDefaultTemplate
from .docker_management import create_container, check_existing, remove_all_existing_container

# Create your views here.
@login_required
def home(request, pk=None):
    if pk == None:
        try:
            get_default = request.user.default_template
        except ObjectDoesNotExist:
            return redirect('user_profile')

        if check_existing(request.user):
            return render(request, 'shell.html')
        else:
            create_container(request.user)
            return render(request, 'shell.html')
    else:
        remove_all_existing_container(request.user)
        create_container(request.user, template=ContainerTemplate.objects.get(pk=pk))

    return render(request, 'shell.html')

@method_decorator(login_required, name='dispatch')
class ContainerCreateView(BSModalCreateView):
    template_name = 'modalForms/create_container_template.html'
    form_class = ContainerTemplateModalForm
    success_message = 'Success: Template was created.'
    success_url = reverse_lazy('user_profile')
    
    def form_valid(self, form):
        if not self.request.is_ajax():
            templ = form.save(commit=False)
            templ.owner = User.objects.get(pk=self.request.user.pk)
            t = templ.save()
            try:
                # call the method to try and cause an error
                get_default = self.request.user.default_template
            except ObjectDoesNotExist:
                # create default template
                default_templ = UserDefaultTemplate(user = User.objects.get(pk=self.request.user.pk), template = ContainerTemplate.objects.get(pk=templ.pk))
                default_templ.save()
        return super(ContainerCreateView, self).form_valid(form)

@method_decorator(login_required, name='dispatch')
class UserUpdateView(BSModalUpdateView):
    model = User
    template_name = 'modalForms/edit_user.html'
    form_class = UserUpdateForm
    success_message = 'Success: User was updated.'
    success_url = reverse_lazy('user_profile')

@login_required
def update_default_template(request, pk):
    templ = get_object_or_404(ContainerTemplate, pk=pk)
    if request.user.pk == templ.owner.pk:
        default_templ = request.user.default_template
        default_templ.template = ContainerTemplate.objects.get(pk=templ.pk)
        default_templ.save()
    return redirect('user_profile')

@login_required
def container_template_del(request, pk):
    templ = get_object_or_404(ContainerTemplate, pk=pk)
    if request.user.pk == templ.owner.pk:
        ContainerTemplate.objects.filter(id=templ.id).delete()
        return redirect('user_profile')
    return redirect('home')

@login_required
def user_profile(request, pk=None):
    if pk != None and request.user.is_superuser and request.user.pk != int(pk):
        user = get_object_or_404(User, pk=pk)
        
        return render(request, 'user_profile.html', {'user': user})
    return render(request, 'user_profile.html', {'user': request.user})

@login_required
def container_template_new(request):
    if request.method == "POST":
        form = ContainerTemplateForm(request.POST)
        if form.is_valid():
            templ = form.save(commit=False)
            templ.save()
            return redirect('home')
    else:
        form = ContainerTemplateForm()
        #return render(request, '')

@login_required
def set_default_container(request):
    if request.method == "POST":
        form = DefaultContainerTemplateForm(request.POST)
        if form.is_valid():
            def_container = form.save(commit=False)
            def_container.owner = get_object_or_404(User, pk=request.user.pk)
            def_container.save()
            return redirect('user_profile')

def test(request):
    return render(request, 'test.html')
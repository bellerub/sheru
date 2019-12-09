from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from .forms import DefaultContainerTemplateForm, ContainerTemplateForm, ContainerTemplateModalForm, UserUpdateForm, CustomUserCreationForm
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
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserCreateView(BSModalCreateView):
    template_name = 'modalForms/new_user.html'
    form_class = CustomUserCreationForm
    success_message = 'Success: User was created.'
    success_url = reverse_lazy('list_users')
    
    def form_valid(self, form):
        if not self.request.is_ajax():
            u = form.save(commit=False)
            u = u.save()
        return super(UserCreateView, self).form_valid(form)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserDeleteView(BSModalDeleteView):
    model = User
    template_name = 'modalForms/delete_user.html'
    success_message = 'Success: User was deleted.'
    success_url = reverse_lazy('list_users')

@method_decorator(login_required, name='dispatch')
class UserUpdateView(BSModalUpdateView):
    model = User
    template_name = 'modalForms/edit_user.html'
    form_class = UserUpdateForm
    success_message = 'Success: User was updated.'

    def get_success_url(self):
        if self.request.user.pk == self.object.id:
            return reverse_lazy('user_profile')
        return reverse_lazy('user_detail', kwargs={'pk': self.object.id})

@login_required
def update_default_template(request, pk):
    templ = get_object_or_404(ContainerTemplate, pk=pk)
    if request.user.pk == templ.owner.pk:
        default_templ = request.user.default_template
        default_templ.template = ContainerTemplate.objects.get(pk=templ.pk)
        default_templ.save()
        return redirect('user_profile')
    if request.user.is_superuser:
        default_templ = templ.owner.default_template
        default_templ.template = templ
        default_templ.save()
        return redirect('user_detail', pk=templ.owner.pk)
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
        return render(request, 'user_profile.html', {'u': user})
    return render(request, 'user_profile.html', {'u': request.user})

#@login_required
#def set_default_container(request):
#    if request.method == "POST":
#        form = DefaultContainerTemplateForm(request.POST)
#        if form.is_valid():
#            def_container = form.save(commit=False)
#            def_container.owner = get_object_or_404(User, pk=request.user.pk)
#            def_container.save()
#            return redirect('user_profile')

@login_required
def list_users(request):
    if request.user.is_superuser:
        return render(request, 'list_users.html', {'users': User.objects.all().order_by('email') })
    return redirect('user_profile')
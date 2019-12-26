from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from .forms import DefaultContainerTemplateForm, ContainerTemplateModalForm, UserUpdateForm, CustomUserCreationForm
from .models import User, ContainerTemplate, UserDefaultTemplate
from .docker_management import get_running_containers, kill_container, ContainerPermissionDenied
import uuid

# Create your views here.
@login_required
def home(request, pk=None):
    try:
        get_default = request.user.default_template
    except ObjectDoesNotExist:
        return redirect('user_profile')

    # Create session guid, if it doesn't yet exist
    if 'uid' not in request.session:
        request.session['uid'] = str(uuid.uuid4())
    session_uid = request.session.get('uid')
    print(str(session_uid))
    
    # Get Template ID
    template_id = get_default.template.id
    if pk != None:
        try:
            template_id=ContainerTemplate.objects.get(pk=pk).id
        except ContainerTemplate.DoesNotExist:
            return redirect('user_profile')
    return render(request, 'shell.html', {'uid': session_uid, 'ctid': template_id})

@method_decorator(login_required, name='dispatch')
class ContainerCreateView(BSModalCreateView):
    template_name = 'modalForms/modify_container_template.html'
    form_class = ContainerTemplateModalForm
    success_message = 'Success: Template was created.'
    #success_url = reverse_lazy('user_profile')
    
    def get_success_url(self):
        if 'pk' in self.kwargs and self.request.user.is_superuser:
            return reverse_lazy('user_detail', kwargs={'pk': self.kwargs['pk']})
        return reverse_lazy('user_profile')
        
    def form_valid(self, form):
        if not self.request.is_ajax():
            if 'pk' in self.kwargs and self.request.user.is_superuser:
                uid = self.kwargs['pk']
            else:
                uid = self.request.user.pk
            templ = form.save(commit=False)
            templ.owner = User.objects.get(pk=uid)
            t = templ.save()
            try:
                # call the method to try and cause an error
                get_default = User.objects.get(pk=uid).default_template
            except ObjectDoesNotExist:
                # create default template
                default_templ = UserDefaultTemplate(user = User.objects.get(pk=uid), template = ContainerTemplate.objects.get(pk=templ.pk))
                default_templ.save()
        return super(ContainerCreateView, self).form_valid(form)

@method_decorator(login_required, name='dispatch')
class ContainerUpdateView(UserPassesTestMixin, BSModalUpdateView):
    model = ContainerTemplate
    template_name = 'modalForms/modify_container_template.html'
    form_class = ContainerTemplateModalForm
    success_message = 'Success: Container template was updated.'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.pk == self.get_object().owner.pk

    def get_success_url(self):
        if self.request.user.pk == self.object.owner.id:
            return reverse_lazy('user_profile')
        return reverse_lazy('user_detail', kwargs={'pk': self.object.owner.id})

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserCreateView(BSModalCreateView):
    template_name = 'modalForms/new_user.html'
    form_class = CustomUserCreationForm
    success_message = 'Success: User was created.'
    success_url = reverse_lazy('admin')
    
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
    success_url = reverse_lazy('admin')

@method_decorator(login_required, name='dispatch')
class UserUpdateView(UserPassesTestMixin, BSModalUpdateView):
    model = User
    template_name = 'modalForms/edit_user.html'
    form_class = UserUpdateForm
    success_message = 'Success: User was updated.'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.pk == self.get_object().pk

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
        messages.success(request, "Template was deleted")
        return redirect('user_profile')
    return redirect('home')

@login_required
def user_profile(request, pk=None):
    if pk != None and request.user.is_superuser and request.user.pk != int(pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, 'user_profile.html', {'u': user, 'running_containers': get_running_containers(user_pk=user.pk)})
    return render(request, 'user_profile.html', {'u': request.user, 'running_containers': get_running_containers(user_pk=request.user.pk)})

@login_required
def admin(request):
    if request.user.is_superuser:
        c = get_running_containers()
        return render(request, 'admin.html', {'users': User.objects.all().order_by('email'), 'running_containers': c })
    return redirect('user_profile')

@login_required
def kill_user_container(request, container_id):
    if request.user.is_superuser or any(c['id'] == container_id for c in get_running_containers(user_pk=request.user.pk)):
        try:
            kill_container(container_id)
            messages.success(request, "Container with id \"" + container_id[:10] + "\" was successfully removed")
        except ContainerPermissionDenied:
            messages.error(request, "You don't have permission to delete this container.")
        except:
            messages.error(request, "Container not found.")
        return redirect(request.META['HTTP_REFERER'])
    return redirect('user_profile')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DefaultContainerTemplateForm, ContainerTemplateForm

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

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



def test(request):
    return render(request, 'test.html')

def shell(request):
    return render(request, 'shell.html', {'session_id': request.session})
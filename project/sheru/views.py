from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')


def test(request):
    return render(request, 'test.html')

def shell(request):
    return render(request, 'shell.html', {'session_id': request.session})
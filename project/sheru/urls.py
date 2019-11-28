from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    url(r'^$', views.home, name='home'),
    url(r'^test/$', views.test, name='test'),
    
    # Authentication
    url(r'^login/$', auth_views.LoginView.as_view(), {'template_name': 'auth/login.html'}, name='login'),
    #url(r'^logout/$', auth_views.logout, {'template_name': 'auth/logout.html'}, name='logout'),
]
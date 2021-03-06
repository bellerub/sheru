from django.conf.urls import url, include
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    url(r'^$', views.home, name='home'),
    url(r'^(?P<pk>\d+)/$', views.home, name='shell'),

    # User Management
    url(r'^profile/$', views.user_profile, name='user_profile'),
    url(r'^profile/(?P<pk>\d+)/$', views.user_profile, name='user_detail'),
    path('profile/update/<int:pk>', views.UserUpdateView.as_view(), name='update_profile'),

    # Container Template Management
    path('create_container_template/', views.ContainerCreateView.as_view(), name='create_container_template'),
    path('container/update/<int:pk>', views.ContainerUpdateView.as_view(), name='update_template'),
    path('create_container_template/<int:pk>', views.ContainerCreateView.as_view(), name='create_container_template_adv'),
    url(r'^container_template/del/(?P<pk>\d+)/$', views.container_template_del, name='del_container_template'),
    url(r'^default_template/update/(?P<pk>\d+)/$', views.update_default_template, name='update_default_template'),

    # Authentication
    url(r'^login/$', views.login, name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),

    # Admin
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^rm/cid/(?P<container_id>\w+)/$', views.kill_user_container, name='remove_cid'),

    # User Management
    path('new_user/', views.UserCreateView.as_view(), name='new_user'),
    path('delete/<int:pk>', views.UserDeleteView.as_view(), name='delete_user')
]
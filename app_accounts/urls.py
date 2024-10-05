from django.urls import re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # AUTHENTICATION
    re_path(r'^account/login/?$', views.UserLoginView.as_view(), name='login'),
    re_path(r'^account/logout/?$', views.logout_view, name='logout'),
    re_path(r'^account/register/?$', views.register, name='register'),
]



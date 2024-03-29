from django.urls import path
from django.contrib.auth import views as auth_views
from .views import LoginView
from . import views

urlpatterns = [
    path('register/', views.register, name='users-register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='users-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='users-logout'),
]
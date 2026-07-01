from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_register, name='login_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
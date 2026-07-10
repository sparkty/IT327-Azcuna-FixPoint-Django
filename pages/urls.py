from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_register, name='login_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('create_issue/', views.create_issue, name='create_issue'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('issue/<int:issue_id>/add-comment/', views.add_comment, name='add_comment'),
    path('issue/<int:issue_id>/update-status/', views.update_status, name='update_status'),
    path('issue/<int:issue_id>/request-deletion/', views.request_deletion, name='request_deletion'),
]
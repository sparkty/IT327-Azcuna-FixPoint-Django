from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_register, name='login_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/open/', views.open_notification, name='open_notification'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/delete-read/', views.delete_read_notifications, name='delete_read_notifications'),
    path('logout/', views.logout_view, name='logout'),
    path('create_issue/', views.create_issue, name='create_issue'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('issue/<int:issue_id>/add-comment/', views.add_comment, name='add_comment'),
    path('issue/<int:issue_id>/update-status/', views.update_status, name='update_status'),
    path('issue/<int:issue_id>/request-deletion/', views.request_deletion, name='request_deletion'),
    path('deletion-request/<int:delete_request_id>/accept/', views.accept_deletion_request, name='accept_deletion_request'),
    path('deletion-request/<int:delete_request_id>/cancel/', views.cancel_deletion_request, name='cancel_deletion_request'),
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.profile_change_password, name='profile_change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]

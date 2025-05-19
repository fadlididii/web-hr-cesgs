from django.urls import path
from . import views

urlpatterns = [
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('all/', views.AllNotificationsView.as_view(), name='all_notifications'),
    path('api/unread-count/', views.api_unread_count, name='api_unread_count'),
]
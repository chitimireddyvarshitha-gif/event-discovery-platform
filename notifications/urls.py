from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('read/<int:notification_id>/', views.mark_as_read, name='mark_read'),
    path('unread-count/', views.unread_count_api, name='unread_api'),
]

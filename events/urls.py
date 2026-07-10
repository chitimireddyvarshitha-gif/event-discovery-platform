from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('create/', views.event_create, name='create'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('<int:event_id>/participants/', views.event_participants, name='participants'),
    path('<int:event_id>/edit/', views.event_edit, name='edit'),
    path('<int:event_id>/delete/', views.event_delete, name='delete'),
]

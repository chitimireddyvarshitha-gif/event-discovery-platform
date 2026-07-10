from django.urls import path

from . import views

app_name = 'registrations'

urlpatterns = [
    path('', views.my_registrations, name='my_registrations'),
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('approve/<int:registration_id>/', views.approve_registration, name='approve_registration'),
    path('reject/<int:registration_id>/', views.reject_registration, name='reject_registration'),
]

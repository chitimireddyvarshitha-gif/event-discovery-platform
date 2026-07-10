from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('events', views.EventViewSet, basename='event')
router.register('registrations', views.RegistrationViewSet, basename='registration')
router.register('tickets', views.TicketViewSet, basename='ticket')
router.register('notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]

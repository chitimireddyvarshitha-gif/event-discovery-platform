from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, OrganizerViewSet, EventViewSet, StaffViewSet, change_password

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'organizers', OrganizerViewSet)
router.register(r'events', EventViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('change-password/', change_password),
]
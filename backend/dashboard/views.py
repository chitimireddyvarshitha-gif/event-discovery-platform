from django.shortcuts import render
from rest_framework import viewsets
from .models import User, Organizer, Event, Staff
from .serializers import UserSerializer, OrganizerSerializer, EventSerializer, StaffSerializer

# ADD THESE IMPORTS
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
import json


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OrganizerViewSet(viewsets.ModelViewSet):
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


# ADD THIS FUNCTION BELOW StaffViewSet

@login_required
def change_password(request):

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required."})

    data = json.loads(request.body)

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    user = request.user

    if not user.check_password(old_password):
        return JsonResponse({
            "success": False,
            "message": "Old password is incorrect."
        })

    user.set_password(new_password)
    user.save()

    update_session_auth_hash(request, user)

    return JsonResponse({
        "success": True,
        "message": "Password changed successfully."
    })
def home(request):
    return render(request, "dashboard/admin_dashboard.html")
from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from events.models import Event
from registrations.models import Registration
from tickets.models import Ticket
from notifications.models import Notification

from .serializers import (
    UserSerializer, RegisterSerializer, EventSerializer,
    RegistrationSerializer, TicketSerializer, NotificationSerializer
)
from .permissions import IsOrganizerOrReadOnly, IsAttendee, IsOrganizer

User = get_user_model()


class RegisterView(APIView):
    """POST /api/register/ - Register a new user and return a Token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user.role == 'organizer':
                return Response({
                    'message': 'Your organizer account has been created successfully and is pending approval from a super admin.',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /api/login/ - Authenticate credentials and return a Token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            if user.role == 'organizer' and not user.is_approved:
                return Response({'error': 'Your organizer account is pending approval from a super admin.'}, status=status.HTTP_403_FORBIDDEN)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(APIView):
    """GET /api/profile/ - Retrieve user profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class EventViewSet(viewsets.ModelViewSet):
    """GET, POST, PUT, DELETE /api/events/ - Manage Event instances."""
    queryset = Event.objects.all().select_related('organizer')
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def get_queryset(self):
        # Allow category filtering in API list
        queryset = self.queryset
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class RegistrationViewSet(viewsets.ModelViewSet):
    """GET, POST /api/registrations/ - Register for events and view booking lists."""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'organizer':
            # Organizers see registrations for their events
            return Registration.objects.filter(event__organizer=user).select_related('user', 'event')
        # Attendees see their own registrations
        return Registration.objects.filter(user=user).select_related('user', 'event')

    def get_permissions(self):
        if self.action == 'create':
            return [IsAttendee()]
        return super().get_permissions()




class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/tickets/ - View generated ticket passes."""
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'organizer':
            # Organizers see tickets issued for their events
            return Ticket.objects.filter(registration__event__organizer=user).select_related('registration', 'registration__user', 'registration__event')
        # Attendees see their own tickets
        return Ticket.objects.filter(registration__user=user).select_related('registration', 'registration__user', 'registration__event')


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/notifications/ - View in-app alerts."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='read')
    def mark_as_read(self, request, pk=None):
        """POST /api/notifications/{id}/read/ - Mark a notification as read."""
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'success': True, 'message': 'Notification marked as read.'})

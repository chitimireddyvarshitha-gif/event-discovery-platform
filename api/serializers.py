from django.contrib.auth import get_user_model
from rest_framework import serializers

from events.models import Event
from registrations.models import Registration
from tickets.models import Ticket
from notifications.models import Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serialize User profiles."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile_number', 'role', 'full_name']
        read_only_fields = ['id', 'username', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    """Validate signups and create User instances."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'mobile_number', 'role', 'full_name']

    def validate_role(self, value):
        if value not in ['attendee', 'organizer']:
            raise serializers.ValidationError("Role must be either 'attendee' or 'organizer'.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            mobile_number=validated_data.get('mobile_number', ''),
            role=validated_data.get('role', 'attendee'),
            full_name=validated_data.get('full_name', '')
        )
        return user


class EventSerializer(serializers.ModelSerializer):
    """Serialize public Event listings."""
    organizer = UserSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'event_name', 'description', 'category', 'category_display',
            'date', 'venue', 'ticket_price', 'ticket_price_vip', 'ticket_price_premium',
            'capacity', 'banner_image', 'department', 'agenda', 'contact_email', 'contact_phone', 'created_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at']


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialize registrations and enforce business validations."""
    user = UserSerializer(read_only=True)
    event_detail = EventSerializer(source='event', read_only=True)
    ticket_type = serializers.CharField(required=False, default='general')
    payment_details = serializers.CharField(read_only=True)
    card_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    card_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Registration
        fields = [
            'id', 'user', 'event', 'event_detail', 'registration_date', 'status',
            'ticket_type', 'payment_details', 'card_number', 'card_name'
        ]
        read_only_fields = ['id', 'user', 'registration_date', 'status', 'payment_details']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        user = request.user
        event = data.get('event')
        
        ticket_type = request.data.get('ticket_type', 'general').lower()
        if ticket_type not in ['general', 'vip', 'premium']:
            ticket_type = 'general'

        # Role constraint
        if user.role != 'attendee' or user.is_superuser:
            raise serializers.ValidationError("Only standard attendees can register for events.")

        # Capacity constraint (only confirmed bookings consume capacity)
        active_regs = Registration.objects.filter(event=event, status='confirmed').count()
        if active_regs >= event.capacity:
            raise serializers.ValidationError("This event has reached its maximum capacity.")

        # Uniqueness constraint
        if Registration.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You have already registered for this event.")

        # Pricing & Payment Validation
        price = event.ticket_price
        if ticket_type == 'vip':
            price = event.ticket_price_vip
        elif ticket_type == 'premium':
            price = event.ticket_price_premium

        if price > 0:
            card_number = request.data.get('card_number', '').strip()
            card_name = request.data.get('card_name', '').strip()
            if not card_number or not card_name:
                raise serializers.ValidationError("Payment is required for this ticket tier. Please provide both card_number and card_name.")
            # Remove any spaces from card number before validation
            card_number_clean = card_number.replace(' ', '')
            if not card_number_clean.isdigit() or len(card_number_clean) < 13:
                raise serializers.ValidationError("Invalid card number. Please provide a valid card number of at least 13 digits.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        event = validated_data['event']
        
        ticket_type = request.data.get('ticket_type', 'general').lower()
        if ticket_type not in ['general', 'vip', 'premium']:
            ticket_type = 'general'
            
        price = event.ticket_price
        if ticket_type == 'vip':
            price = event.ticket_price_vip
        elif ticket_type == 'premium':
            price = event.ticket_price_premium
            
        status = 'pending' if price > 0 else 'confirmed'
        
        if price > 0:
            card_name = request.data.get('card_name', '').strip()
            card_number = request.data.get('card_number', '').strip().replace(' ', '')
            payment_details = f"Cardholder: {card_name} | Card: **** **** **** {card_number[-4:] if len(card_number) >= 4 else '1111'}"
        else:
            payment_details = "Free Event (No Payment Required)"
            
        return Registration.objects.create(
            user=user,
            event=event,
            status=status,
            ticket_type=ticket_type,
            payment_details=payment_details
        )


class TicketSerializer(serializers.ModelSerializer):
    """Serialize Ticket passes."""
    registration_detail = RegistrationSerializer(source='registration', read_only=True)
    ticket_type_display = serializers.CharField(source='get_ticket_type_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'ticket_code', 'registration', 'registration_detail',
            'ticket_type', 'ticket_type_display', 'issued_at'
        ]
        read_only_fields = ['id', 'ticket_number', 'ticket_code', 'issued_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serialize system alerts."""
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'title', 'message', 'created_at']

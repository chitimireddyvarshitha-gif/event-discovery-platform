from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'event_name',
            'description',
            'category',
            'date',
            'venue',
            'ticket_price',
            'ticket_price_vip',
            'ticket_price_premium',
            'capacity',
            'banner_image',
            'department',
            'agenda',
            'contact_email',
            'contact_phone',
        )
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'agenda': forms.Textarea(attrs={'rows': 3}),
        }

from django.contrib import admin
from .models import User, Organizer, Event

admin.site.register(User)
admin.site.register(Organizer)
admin.site.register(Event)
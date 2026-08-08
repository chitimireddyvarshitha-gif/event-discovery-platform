from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=15, required=True)
    
    ROLE_CHOICES_REGISTRATION = (
        ('attendee', 'Attendee'),
        ('organizer', 'Organizer'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES_REGISTRATION, required=True)

    class Meta:
        model = User
        fields = ('full_name', 'username', 'email', 'mobile_number', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.mobile_number = self.cleaned_data['mobile_number']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'mobile_number', 'interests', 'profile_picture')

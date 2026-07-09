from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20)
    photo = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Organizer(models.Model):
    organization = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.organization


class Event(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=150)
    image = models.URLField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="Active")

    manage_users = models.BooleanField(default=False)
    manage_events = models.BooleanField(default=False)
    manage_organizers = models.BooleanField(default=False)
    analytics = models.BooleanField(default=False)
    reports = models.BooleanField(default=False)
    delete_users = models.BooleanField(default=False)
    delete_events = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)

    def __str__(self):
        return self.name
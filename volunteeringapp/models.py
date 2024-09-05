from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Creating the model for all the users that will be using this application
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ACCOUNT_TYPES = [
        ('participant', 'Participant'),
        ('organiser', 'Organiser'),
        ('administrator', 'Administrator'),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='participant')

    def __str__(self):
        return self.user.username
    
# Category tags that will help to categorise the events
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# creating the organisers model
class Organiser(models.Model):
    app_user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    organisation_name = models.CharField(max_length=255)
    organisation_writeup = models.TextField()
    organisation_email = models.EmailField(unique=True)

    def __str__(self):
        return self.organisation_name

#creating the event models with the following fields
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)
    max_participants = models.IntegerField()
    preference_tags = models.ManyToManyField('Category', related_name='events', blank=True)
    rating = models.IntegerField(default=0)
    event_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    organiser = models.ForeignKey(Organiser, related_name='events', on_delete=models.CASCADE)
    signups_locked = models.BooleanField(default=False)
    withdrawals_locked = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})

# create the participant model
class Participant(models.Model):
    app_user = models.OneToOneField(AppUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    past_events = models.ManyToManyField('Event', related_name='past_participants', blank=True)
    upcoming_events = models.ManyToManyField('Event', through='EventParticipation', related_name='upcoming_participants', blank=True)
    experience_level = models.IntegerField(default=0)
    category_preferences = models.ManyToManyField('Category', related_name='participants', blank=True)

    def __str__(self):
        return self.name

    def update_experience_level(self):
        self.experience_level = sum(event.rating for event in self.past_events.all())
        self.save()

# this model will check on the status of the event and log the participants 
class EventParticipation(models.Model):
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('not_signed_up', 'Not Signed Up'),
        ('signed_up', 'Signed Up'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_signed_up')

    def __str__(self):
        return f"{self.participant.name} - {self.event.title} ({self.get_status_display()})"



#the following chat room and chat messages will help to save the messages into the database so that it can log the chat history
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message}"
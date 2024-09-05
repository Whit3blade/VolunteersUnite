from django import forms
from django.contrib.auth.models import User
from .models import *


# user sign up form management
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    ACCOUNT_TYPES = [
        ('participant', 'Participant'),
        ('organiser', 'Organiser'),
        ('administrator', 'Administrator'),
    ]
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)
    name = forms.CharField(max_length=100, label='Name')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'account_type')

# customising the participants profile form and 
# enable them to make mulitple selections for the category preferences
class ParticipantProfileForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'date_of_birth', 'category_preferences']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'category_preferences': forms.CheckboxSelectMultiple(),
        }

# organiser from to customise the organisations detail and this will be rendered on the organisers upcoming page
class OrganiserForm(forms.ModelForm):
    class Meta:
        model = Organiser
        fields = ['organisation_name', 'organisation_writeup', 'organisation_email']

    def clean(self):
        cleaned_data = super().clean()
        account_type = self.initial.get('account_type')
        
        if account_type == 'organiser':
            organisation_email = cleaned_data.get('organisation_email')
            if not organisation_email:
                self.add_error('organisation_email', 'Organisation Email is required for organisers.')
        return cleaned_data

# Form to create and manage the new and exisiting events 
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'max_participants', 'preference_tags', 'rating', 'event_image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    preference_tags = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

# category form is the same as the category tags and allow for the admin to create them
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name

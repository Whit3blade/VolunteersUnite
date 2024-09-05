from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, JsonResponse
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib import messages
from rest_framework import generics
from .serializers import *
from .api import *
from .models import *
from .forms import *
import random

def index(request):
    if request.user.is_authenticated:
        try:
            participant = Participant.objects.get(app_user=request.user.appuser)
            preferences = participant.category_preferences.all()
            # Fetch events matching the user's preferences
            if preferences.exists():
                matching_events = Event.objects.filter(preference_tags__in=preferences).distinct()
                # Annotate events with the number of matching tags and show up to 10 events so as to not flood the index page
                matching_events = matching_events.annotate(
                    num_matches=Count('preference_tags')
                ).order_by('-num_matches', 'date')[:10] 
                return render(request, 'volunteeringapp/index.html', {
                    'events': matching_events
                })
            else:
                # No preferences selected then select 10 random events and prompt user to select
                random_events = Event.objects.order_by('?')[:10]  
                return render(request, 'volunteeringapp/index.html', {
                    'events': random_events,
                    'prompt': 'Please update your preferences to see more relevant events.'  
                    # ^^^^^^^^^^^^ method to encourage the user to customise
                })
        except Participant.DoesNotExist: # if it is a random user it will just randomly find 10 events
            random_events = Event.objects.order_by('?')[:10]
            return render(request, 'volunteeringapp/index.html', {
                'events': random_events,
                'prompt': 'Please update your preferences to see more relevant events.' 
            })
    else:
        # if it is a random user it will just randomly find 10 events
        random_events = Event.objects.order_by('?')[:10]
        return render(request, 'volunteeringapp/index.html', {
            'events': random_events
        })
################################################
## Log in credentials setting
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            return render(request, 'volunteeringapp/incorrect.html')
    else:
        return render(request, 'volunteeringapp/login.html')

# User creation handler it will upload to the database adhering to the models that was initalised
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        account_type = request.POST.get('account_type')
        name = request.POST.get('name')
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            group, created = Group.objects.get_or_create(name=account_type)
            group.user_set.add(user)
            app_user = AppUser.objects.create(user=user, account_type=account_type)

            if account_type == 'participant':
                Participant.objects.create(
                    app_user=app_user,
                    name=name
                )
            elif account_type == 'organiser':
                organiser_form = OrganiserForm(request.POST)
                if organiser_form.is_valid():
                    Organiser.objects.create(
                        app_user=app_user,
                        organisation_name=name,
                        organisation_writeup=organiser_form.cleaned_data['organisation_writeup'],
                        organisation_email=organiser_form.cleaned_data['organisation_email']
                    )
                else:
                    return render(request, 'volunteeringapp/register.html', {
                        'user_form': user_form,
                        'organiser_form': organiser_form,
                        'registered': registered
                    })
            # automatically log in without having the user to log in after creating the account
            login(request, user)
            registered = True
            return redirect('index')
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()
        organiser_form = OrganiserForm()  

    return render(request, 'volunteeringapp/register.html', {
        'user_form': user_form,
        'organiser_form': organiser_form,  # Pass it to the template
        'registered': registered
    })

# View to simply log the user out
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect('/')

#will require authentication prior to account deletion
@login_required
def delete_account(request):
    user = request.user
    if request.method == 'POST':
        if hasattr(user, 'appuser'):
            app_user = user.appuser
            if app_user.account_type == 'participant':
                Participant.objects.filter(app_user=app_user).delete()
            elif app_user.account_type == 'organiser':
                Organiser.objects.filter(app_user=app_user).delete()
            app_user.delete()
        logout(request)
        user.delete()
        return redirect('index') 
    return render(request, 'volunteeringapp/delete_account.html')


##############################################################
## User account customisation

# for organisers
def organiser_profile(request):
    try:
        organiser = Organiser.objects.get(app_user=request.user.appuser)
    except Organiser.DoesNotExist:
        preferred_name = request.user.name  
        organiser = Organiser.objects.create(
            app_user=request.user.appuser,
            organisation_name=preferred_name,  
            organisation_writeup='', 
            organisation_email=request.user.email
        )
    if request.method == 'POST':
        form = OrganiserForm(request.POST, instance=organiser)
        if form.is_valid():
            form.save()
            return redirect('organiser_profile') 
    else:
        form = OrganiserForm(instance=organiser)

    context = {
        'form': form,
        'organisation_name': organiser.organisation_name,
        'organisation_writeup': organiser.organisation_writeup,
    }
    return render(request, 'volunteeringapp/organiser_profile.html', context)

# for participants
def participant_profile(request):
    participant, created = Participant.objects.get_or_create(app_user=request.user.appuser)
    if request.method == 'POST':
        form = ParticipantProfileForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            return redirect('participant_profile')
    else:
        form = ParticipantProfileForm(instance=participant)

    context = {
        'form': form,
        'experience_level': participant.experience_level
    }
    return render(request, 'volunteeringapp/participant_profile.html', context)


################################################
## Organiser event settings
def create_event(request):
    #verify before allowing the user to proceed
    try:
        organiser = Organiser.objects.get(app_user=request.user.appuser)
    except Organiser.DoesNotExist:
        return HttpResponseRedirect(reverse('organiser_profile'))  # Although this is here, the template use django features to not show this option. This is for backup
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organiser = organiser  
            event.save()
            form.save_m2m() 
            return redirect('event_detail', event.id)
    else:
        form = EventForm()

    return render(request, 'volunteeringapp/create_event.html', {'form': form})

# To make any modifications to the event page.
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Check if the logged-in user is the organiser of this event
    if request.user.appuser.account_type == 'organiser' and request.user.appuser.organiser == event.organiser:
        if request.method == 'POST':
            form = EventForm(request.POST, request.FILES, instance=event)
            if form.is_valid():
                form.save()
                return redirect('discover')
        else:
            form = EventForm(instance=event)
        
        return render(request, 'volunteeringapp/edit_event.html', {'form': form, 'event': event})
    else:
        return HttpResponseForbidden("You are not allowed to edit this event.")

#to delete the event
@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the user is an administrator or the event's organiser
    if request.user.appuser.account_type == 'administrator' or event.organiser.app_user == request.user.appuser:
        event.delete()
        return redirect('discover')  # Redirect to the event list or any other page after deletion
    else:
        return HttpResponseForbidden("You are not allowed to delete this event.")
    
@login_required
def toggle_signups_lock(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Ensure the user is the organiser of the event
    if request.user.appuser.account_type == 'organiser' and event.organiser == request.user.appuser.organiser:
        event.signups_locked = not event.signups_locked
        event.save()
    
    return redirect('event_detail', pk=pk)

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    participant = None
    participation = None

    if request.user.is_authenticated:
        try:
            participant = Participant.objects.get(app_user=request.user.appuser)
            participation = EventParticipation.objects.filter(event=event, participant=participant).first()
        except Participant.DoesNotExist:
            participant = None
    if request.method == 'POST':
        if participant:
            if 'signup' in request.POST:
                if event.signups_locked:
                    messages.error(request, 'Sign-ups are locked. You cannot join this event.')
                elif participation:
                    messages.error(request, 'You are already signed up for this event.')
                elif event.upcoming_participants.count() >= event.max_participants:
                    messages.error(request, 'Maximum participant limit reached for this event.')
                else:
                    EventParticipation.objects.create(participant=participant, event=event)
                    messages.success(request, 'Successfully signed up for the event.')
            elif 'withdraw' in request.POST:
                if event.signups_locked:
                    messages.error(request, 'Withdrawals are locked. You cannot leave this event.')
                elif not participation:
                    messages.error(request, 'You are not signed up for this event.')
                else:
                    participation.delete()
                    messages.success(request, 'You have successfully withdrawn from the event.')
        elif 'close_event' in request.POST:
            print("Debug: 'close_event' triggered.")
            print(f"Debug: Logged-in user: {request.user.username}, Account type: {request.user.appuser.account_type}")

            if request.user.appuser.account_type == 'organiser':
                print("Debug: User is an organiser.")
                if event.organiser.app_user == request.user.appuser:
                    print(f"Debug: User is the event organiser for event '{event.title}'.")
                    if not event.closed:
                        print("Debug: Event is currently open. Proceeding to close the event.")
                        event.closed = True
                        event.save()
                        # Update experience levels for all participants
                        for participant in event.upcoming_participants.all():
                            # Award the participants with experience points
                            participant.experience_level += event.rating
                            participant.save()
                            # Add the closed event to the participant's past events
                            participant.past_events.add(event)
                        messages.success(request, 'Event closed and experience levels updated.')
                    else:
                        print("Debug: Event is already closed.")
                        messages.error(request, 'Event is already closed.')
                else:
                    print("Debug: User is NOT the event organiser.")
            else:
                print("Debug: User is NOT an organiser.")

        return redirect('event_detail', pk=pk)

    participants = EventParticipation.objects.filter(event=event)

    return render(request, 'volunteeringapp/event_detail.html', {
        'event': event,
        'remaining_slots': event.max_participants - event.upcoming_participants.count(),
        'user_participation': participation,
        'signups_locked': event.signups_locked,
        'participants': participants,
        'event_closed': event.closed,
    })


# for the admin to add remove or rename the category / preference tags.
def manage_categories(request):
    categories = Category.objects.all()
    form = CategoryForm()

    if request.method == 'POST':
        if 'rename_category' in request.POST:
            category_id = request.POST.get('category_id')
            new_name = request.POST.get('new_name')
            category = get_object_or_404(Category, id=category_id)

            if Category.objects.filter(name=new_name).exists():
                messages.error(request, "A category with this name already exists.")
            else:
                category.name = new_name
                category.save()
                messages.success(request, "Category renamed successfully.")
            return redirect('manage_categories')

        elif 'add_category' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_categories')

        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            events_using_category = Event.objects.filter(preference_tags=category).exists()

            if events_using_category:
                messages.error(request, "This category is associated with one or more events and cannot be deleted.")
            else:
                category.delete()
                messages.success(request, "Category deleted successfully.")
            return redirect('manage_categories')

    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'volunteeringapp/manage_categories.html', context)


################################################
## Straightforward links

def whyvolunteer(request):
    return render(request, 'volunteeringapp/whyvolunteer.html')

def about(request):
    return render(request, 'volunteeringapp/about.html')


# Handler to show and render all the events associated 
def discover(request):
    is_admin_or_organiser = False
    if request.user.is_authenticated:
        if request.user.appuser.account_type in ['administrator', 'organiser']:
            is_admin_or_organiser = True

    # Default to showing only active events for participants or unauthenticated users
    events = Event.objects.filter(closed=False) if not is_admin_or_organiser else Event.objects.all()

    # Check if the user is an administrator or organiser as there is a feature to see past and active events
    if is_admin_or_organiser:
        event_status = request.GET.get('status', 'active')
        if event_status == 'closed':
            events = events.filter(closed=True)
        else:
            events = events.filter(closed=False)

    # filter by category tags
    category_filter = request.GET.get('category')
    if category_filter:
        events = events.filter(preference_tags__id=category_filter)

    # Apply sorting
    sort_option = request.GET.get('sort_by', 'date_asc')  # << sorted by date ascending default

    if sort_option == 'date_asc':
        events = events.order_by('date')
    elif sort_option == 'date_desc':
        events = events.order_by('-date')
    elif sort_option == 'title_asc':
        events = events.order_by('title')
    elif sort_option == 'title_desc':
        events = events.order_by('-title')

    return render(request, 'volunteeringapp/browse.html', {
        'events': events,
        'is_admin_or_organiser': is_admin_or_organiser,
        'categories': Category.objects.all(), 
        'status': event_status if is_admin_or_organiser else 'active',  
        'sort_option': sort_option 
    })

# View upcoming and all past events, along with the calendar
def your_events(request):
    if not request.user.is_authenticated:
        return redirect('login')
     #again this line is handled by the web 
    #template however if the user tries to be funny this will come as a back up
    user = request.user.appuser
    upcoming_events = Event.objects.none()
    past_events = Event.objects.none()
    if user.account_type == 'participant':
        # only able to see events that the participant joined
        try:
            participant = Participant.objects.get(app_user=user)
            upcoming_events = Event.objects.filter(
                upcoming_participants=participant,
                closed=False
            )
            past_events = participant.past_events.filter(
                closed=True
            )
        except Participant.DoesNotExist:
            upcoming_events = Event.objects.none()
            past_events = Event.objects.none()
    elif user.account_type == 'organiser':
        #can see all the events they join or they have created
        try:
            organiser = Organiser.objects.get(app_user=user)
            upcoming_events = Event.objects.filter(
                organiser=organiser,
                closed=False
            )
            past_events = Event.objects.filter(
                organiser=organiser,
                closed=True
            )
        except Organiser.DoesNotExist:
            upcoming_events = Event.objects.none()
            past_events = Event.objects.none()
    elif user.account_type == 'administrator':
        # allow admin to see all events
        upcoming_events = Event.objects.filter(closed=False)
        past_events = Event.objects.filter(closed=True)
    else:
        upcoming_events = Event.objects.none()
        past_events = Event.objects.none()
    return render(request, 'volunteeringapp/your_events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    })

# Customising how the events will be rendered on the calendar
def calendar_events(request):
    user = request.user.appuser
    event_list = []
    #in order to not have all organisers on the same colour
    colors = [
        '#FF5733', 
        '#33FF57',  
        '#3357FF',  
        '#FF33A6', 
        '#FF8C33',  
        '#8C33FF',
    ]
    if user.account_type == 'participant':
        participant = Participant.objects.get(app_user=user)
        events = Event.objects.filter(
            upcoming_participants=participant
        ) | Event.objects.filter(
            past_participants=participant
        )
    elif user.account_type == 'organiser':
        organiser = Organiser.objects.get(app_user=user)
        events = Event.objects.filter(organiser=organiser)
    elif user.account_type == 'administrator':
        # Administrators see all events on the calendar
        events = Event.objects.all()
    else:
        events = Event.objects.none()  
    organiser_colors = {}
    for event in events:
        organiser_id = event.organiser_id
        if organiser_id not in organiser_colors:
            organiser_colors[organiser_id] = random.choice(colors)

        event_list.append({
            'title': event.title,
            'start': event.date.isoformat(),
            'url': request.build_absolute_uri(reverse('event_detail', kwargs={'pk': event.pk})),
            'color': organiser_colors[organiser_id],  # Assign the background color
            'textColor': '#000000',  # Set text color to black
        })
    return JsonResponse(event_list, safe=False)

# renders the selected organiser by taking in 2 fields to render on the application
def organiser_upcoming_events_by_name(request, organisation_name):
    organiser = get_object_or_404(Organiser, organisation_name=organisation_name)
    
    upcoming_events = Event.objects.filter(
        organiser=organiser,
        closed=False
    )
    
    return render(request, 'volunteeringapp/organiser_upcoming_events.html', {
        'upcoming_events': upcoming_events,
        'organiser': organiser
    })



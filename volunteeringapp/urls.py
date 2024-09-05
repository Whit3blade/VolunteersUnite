from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from . import api
from .views import *

urlpatterns = [
    path('', views.index, name='index'),
    #account creation phase
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),

    #main content bunch
    path('browse/', views.discover, name='discover'),
    path('whyvolunteer/', views.whyvolunteer, name='whyvolunteer'),
    path('about/', views.about, name='about'),

    # Event settings and browsing
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/toggle_signups_lock/', toggle_signups_lock, name='toggle_signups_lock'),
    path('your-events/', views.your_events, name='your_events'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
    path('organiser-events/<str:organisation_name>/', organiser_upcoming_events_by_name, name='organiser_upcoming_events_by_name'),
    
    # Forms 
    path('organiser_profile/', views.organiser_profile, name='organiser_profile'),
    path('participant_profile/', views.participant_profile, name='participant_profile'),
    path('create_event/', views.create_event, name='create_event'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', delete_event, name='delete_event'),

    # Admin access
    path('manage_categories/', manage_categories, name='manage_categories'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


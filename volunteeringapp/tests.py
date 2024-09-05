from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import *
from .forms import *
from django.core.files.uploadedfile import SimpleUploadedFile

class AppUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.app_user = AppUser.objects.create(user=self.user, account_type='participant')

    def test_app_user_str(self):
        self.assertEqual(str(self.app_user), 'testuser')

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

class OrganiserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.app_user = AppUser.objects.create(user=self.user, account_type='organiser')
        self.organiser = Organiser.objects.create(
            app_user=self.app_user,
            organisation_name='Test Org',
            organisation_writeup='A test organisation',
            organisation_email='org@test.com'
        )

    def test_organiser_str(self):
        self.assertEqual(str(self.organiser), 'Test Org')

class EventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.app_user = AppUser.objects.create(user=self.user, account_type='organiser')
        self.organiser = Organiser.objects.create(
            app_user=self.app_user,
            organisation_name='Test Org',
            organisation_writeup='A test organisation',
            organisation_email='org@test.com'
        )
        self.category = Category.objects.create(name='Test Category')
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date='2024-01-01',
            location='Test Location',
            max_participants=100,
            rating=5,
            organiser=self.organiser,
        )
        self.event.preference_tags.add(self.category)

    def test_event_str(self):
        self.assertEqual(str(self.event), 'Test Event')

    def test_get_absolute_url(self):
        self.assertEqual(self.event.get_absolute_url(), reverse('event_detail', kwargs={'pk': self.event.pk}))

class ParticipantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.app_user = AppUser.objects.create(user=self.user, account_type='participant')
        self.participant = Participant.objects.create(
            app_user=self.app_user,
            name='Test Participant',
            date_of_birth='2000-01-01'
        )

    def test_participant_str(self):
        self.assertEqual(str(self.participant), 'Test Participant')


class EventParticipationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.app_user = AppUser.objects.create(user=self.user, account_type='participant')
        self.participant = Participant.objects.create(app_user=self.app_user, name='Test Participant')
        self.organiser = Organiser.objects.create(
            app_user=self.app_user,
            organisation_name='Test Org',
            organisation_writeup='A test organisation',
            organisation_email='org@test.com'
        )
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date='2024-01-01',
            location='Test Location',
            max_participants=100,
            rating=5,
            organiser=self.organiser
        )
        self.event_participation = EventParticipation.objects.create(
            participant=self.participant,
            event=self.event,
            status='signed_up'
        )

    def test_event_participation_str(self):
        self.assertEqual(
            str(self.event_participation),
            f"{self.participant.name} - {self.event.title} (Signed Up)"
        )

class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.chat_room = ChatRoom.objects.create(name='Test Chat Room')
        self.chat_message = ChatMessage.objects.create(
            room=self.chat_room,
            sender=self.user,
            message='Test Message'
        )

    def test_chat_message_str(self):
        self.assertEqual(str(self.chat_message), f"{self.user.username}: Test Message")


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = self.client_class()

    def test_register_participant(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'testpass',
            'account_type': 'participant',
            'name': 'Test Participant'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Participant.objects.filter(name='Test Participant').exists())


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.app_user = AppUser.objects.create(user=self.user, account_type='participant')
        self.participant = Participant.objects.create(
            app_user=self.app_user,
            name='Test Participant',
            date_of_birth='2000-01-01'
        )
        self.client.login(username='testuser', password='testpass')

    def test_participant_profile(self):
        response = self.client.get(reverse('participant_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Participant')

    def test_organiser_profile(self):
        self.app_user.account_type = 'organiser'
        self.app_user.save()
        self.organiser = Organiser.objects.create(
            app_user=self.app_user,
            organisation_name='Test Org',
            organisation_writeup='A test organisation',
            organisation_email='org@test.com'
        )
        response = self.client.get(reverse('organiser_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Org')

class AuthenticationTests(TestCase):
    def test_login(self):
        User.objects.create_user(username='testuser', password='testpass')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login

    def test_logout(self):
        User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

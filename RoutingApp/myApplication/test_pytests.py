# standard library
import os

# Django
import django

#  pytest was unsatisfied with DJANGO_SETTINGS_MODULE so i had to set it
#  explicitly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RoutingApp.settings')
django.setup()

# third-party
import pytest  # noqa: E402
from allauth.socialaccount.models import SocialAccount  # noqa: E402

# Django
from django.contrib.auth.models import User  # noqa: E402
from django.shortcuts import get_object_or_404  # noqa: E402
from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

# local Django
from RoutingApp.forms import MemoryForm  # noqa: E402

from .models import Memory  # noqa: E402


@pytest.fixture
def user():
    """
    Create a test user.
    """
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def user2():
    """
    Create another test user.
    """
    return User.objects.create_user(username='testuser2', password='testpass2')


@pytest.fixture
def client(user):
    """
    Create a test client and authenticate as the test user.
    """
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_welcome(client):
    """
    Test the welcome view.
    """
    response = client.get(reverse('welcome'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_home(client, user):
    """
    Test the home view.
    """
    client.force_login(user)

    # Create a vk SocialAccount for testing image retrieving
    SocialAccount.objects.create(
        user=user,
        provider='vk',
        extra_data={
            'photo_max_orig':
                'https://i.ytimg.com/vi/XZxu1kiP65w/maxresdefault.jpg'
        }
    )

    client.post(reverse('add_memory'), {
        'place_name': 'Test Place404',
        'comment': 'Test Comment',
        'latitude': 123.456,
        'longitude': 789.012,
        'user': user.id  # Associate the memory with the test user
    })
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert response.context[
               'profile_picture'] == \
           'https://i.ytimg.com/vi/XZxu1kiP65w/maxresdefault.jpg'
    assert response.context['memories'][0].place_name == 'Test Place404'

    # Create a Google SocialAccount for testing image retrieving
    SocialAccount.objects.create(
        user=user,
        provider='google',
        extra_data={'picture': 'https://lookw.ru/9/980/1566944536-1-38.jpg'}
    )
    response = client.get(reverse('home'))
    assert response.context[
               'profile_picture'] == \
           'https://lookw.ru/9/980/1566944536-1-38.jpg'


@pytest.mark.django_db
def test_add_memory(client, user):
    """
    Test the add_memory view.
    """
    response = client.post(reverse('add_memory'), {
        'place_name': 'Test Place',
        'comment': 'Test Comment',
        'latitude': 123.456,
        'longitude': 789.012,
        'user': user.id  # Associate the memory with the test user
    })
    assert response.status_code == 302
    assert response.url == reverse('home')
    assert Memory.objects.filter(place_name='Test Place',
                                 comment='Test Comment', user=user).exists()

    response = client.get(reverse('add_memory'))
    assert isinstance(response.context['form'], MemoryForm)


@pytest.mark.django_db
def test_display_memory(client, user):
    """
    Test the display_memory view.
    """
    memory = Memory.objects.create(
        place_name='Test Place',
        comment='Test Comment',
        latitude=123.456,
        longitude=789.012,
        user=user
    )

    response = client.get(reverse('display_memory', args=[memory.id]))
    assert response.status_code == 200

    form = response.context['form']
    rendered_form = form.as_table()
    assert str(memory.place_name) in rendered_form
    assert str(memory.comment) in rendered_form
    assert str(memory.latitude) in rendered_form
    assert str(memory.longitude) in rendered_form

    response = client.post(reverse('display_memory', args=[memory.id]), {
        'place_name': 'Changed Test Place',
        'comment': 'Changed Test Comment',
        'latitude': 456.123,
        'longitude': 12.789,
        'user': user.id  # Associate the memory with the test user
    })
    assert response.status_code == 302
    assert response.url == reverse('home')

    changed_memory = get_object_or_404(Memory, id=memory.id)
    assert changed_memory.place_name == 'Changed Test Place'
    assert changed_memory.comment == 'Changed Test Comment'
    assert changed_memory.latitude == 456.123
    assert changed_memory.longitude == 12.789


@pytest.mark.django_db
def test_retrieve_memories_for_user(client, user, user2):
    """
    Test retrieving memories for a specific user.
    """
    Memory.objects.create(
        place_name='Test Place 1',
        comment='Test Comment 1',
        latitude=123.456,
        longitude=789.012,
        user=user
    )
    Memory.objects.create(
        place_name='Test Place 2',
        comment='Test Comment 2',
        latitude=1.456,
        longitude=1.012,
        user=user
    )
    memory3 = Memory.objects.create(
        place_name='Test Place user2 1',
        comment='Test Comment user2 1',
        latitude=5.456,
        longitude=6.012,
        user=user2
    )
    memory4 = Memory.objects.create(
        place_name='Test Place user2 2',
        comment='Test Comment user2 2',
        latitude=7.456,
        longitude=8.012,
        user=user2
    )
    mems = list(Memory.objects.filter(user=user2))
    assert mems == [memory3, memory4]

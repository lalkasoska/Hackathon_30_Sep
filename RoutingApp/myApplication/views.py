# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# local Django
from RoutingApp.forms import MemoryForm

from .models import Memory


def welcome(request):
    """
    Renders the welcome page.
    """
    return render(request, 'welcome.html')


@login_required
def home(request):
    """
    Renders the home page with the user's memories.
    """
    user = request.user
    profile_picture = None
    memories = Memory.objects.filter(user=user)

    # Retrieve the profile picture URL based on the authentication provider
    if user.is_authenticated:
        if user.socialaccount_set.filter(provider='google').exists():
            google_provider = user.socialaccount_set.get(provider='google')
            profile_picture = google_provider.extra_data.get('picture')
        elif user.socialaccount_set.filter(provider='vk').exists():
            vk_provider = user.socialaccount_set.get(provider='vk')
            profile_picture = vk_provider.extra_data.get('photo_max_orig')

    context = {
        'user': user,
        'profile_picture': profile_picture,
        'memories': memories,
    }
    return render(request, 'home.html', context)


@login_required
def add_memory(request):
    """
    Renders the page for addition of a new memory.
    """
    if request.method == 'POST':
        form = MemoryForm(request.POST)
        if form.is_valid():
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            place_name = form.cleaned_data['place_name']
            comment = form.cleaned_data['comment']

            # Process the latitude, longitude, place_name, and comment as
            # needed
            # ...

            # Save the memory object
            memory = form.save(commit=False)
            memory.latitude = latitude
            memory.longitude = longitude
            memory.place_name = place_name
            memory.comment = comment
            memory.user = request.user
            memory.save()

            # Redirect to the home page or a success page
            return redirect('home')
    else:
        form = MemoryForm()

    return render(request, 'add_memory.html', {'form': form})


@login_required
def display_memory(request, memory_id):
    """
    Renders the display memory page for a specific memory.
    """
    # Retrieve the memory object based on the memory ID
    memory = get_object_or_404(Memory, id=memory_id)

    if request.method == 'POST':
        form = MemoryForm(request.POST, instance=memory)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MemoryForm(instance=memory)

    # Pass the memory to the template context
    context = {'memory': memory, 'form': form}
    return render(request, 'display_memory.html', context)

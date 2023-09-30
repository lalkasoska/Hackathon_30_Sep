# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# local Django
from RoutingApp.forms import MemoryForm
from RoutingApp.forms import OrderForm

from .models import Memory
from .models import Order

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
    memories = Memory.objects.filter(user=user) #delete
    orders = Order.objects.filter(user=user)


    context = {
        'user': user,
        'orders': orders,
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
def display_memory(request, memory_id): #edited here
    """
    Renders the display memory page for a specific memory.
    """
    # Retrieve the memory object based on the memory ID
    memory = get_object_or_404(Memory, id=memory_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=memory)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = OrderForm(instance=memory)

    # Pass the memory to the template context
    context = {'memory': order, 'form': form}
    return render(request, 'display_memory.html', context)

from django.contrib import admin

# local Django
from .models import Memory
from .models import Order
admin.site.register(Memory)
admin.site.register(Order)

# Register your models here.

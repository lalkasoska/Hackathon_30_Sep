# Django
from django.contrib.auth.models import User
from django.db import models


class Memory(models.Model):
    """
    Model representing a memory.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place_name = models.CharField(max_length=100)
    comment = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the memory.
        """
        return self.place_name

# Create your models here.

class Order(models.Model):
    ord_id = models.AutoField(primary_key= True)
    ord_adress_name = models.CharField(max_length= 100)
    ord_adress_loc = models.CharField(max_length= 100)
    ord_time = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE) #Courier
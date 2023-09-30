# Django
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Order(models.Model):
    ord_id = models.AutoField(primary_key= True)
    ord_adress_name = models.CharField(max_length= 100)
    ord_adress_loc = models.CharField(max_length= 100)
    ord_time = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE) #Courier
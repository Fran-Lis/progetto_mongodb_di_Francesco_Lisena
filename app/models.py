from django.db import models
from django.contrib.auth.models import User
from djongo.models.fields import ObjectIdField 
from django.conf import settings

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    _id = ObjectIdField()
    btc = models.FloatField()
    profit = models.FloatField()

class Order(models.Model):
    Typology_choices = (
        ('sell', 'sell'),
        ('buy', 'buy')
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    typology = models.CharField(max_length=10, choices=Typology_choices)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()
    active = models.BooleanField(default=True)

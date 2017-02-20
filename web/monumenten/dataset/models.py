from django.db import models


# Create your models here.
class Dummy(models.Model):
    klasse = models.IntegerField(primary_key=True)

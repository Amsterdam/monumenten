from django.db import models



class Monument(models.Model):
    """
    Monument model
    """
    id = models.CharField(max_length=255, primary_key=True)
   # monumentnummer = models.IntegerField( default='0')
   # naam = models.CharField(max_length=255, default='')
   # type = models.CharField(max_length=255, default='')
   # status = models.CharField(max_length=255, default='')

    def __str__(self):
        return "Monument {}".format(self.id)
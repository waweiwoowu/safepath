from django.db import models

# Create your models here.
class Earthquake(models.Model):
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    scale = models.DecimalField(max_digits=5, decimal_places=2)
    city = models.TextField(max_length=100)
    level = models.IntegerField()

    def __str__(self):
        return f"{self.date} {self.time} - {self.city} - {self.level}"

class AccidentDensity(models.Model):
    latitude_range = models.DecimalField(max_digits=8, decimal_places=5)
    longitude_range = models.DecimalField(max_digits=8, decimal_places=5)
    fatality = models.IntegerField()
    injure = models.IntegerField()

    def __str__(self):
        return f"{self.latitude_range} {self.longitude_range}"
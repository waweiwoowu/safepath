from django.db import models


class Earthquake(models.Model):
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    magnitude = models.DecimalField(max_digits=5, decimal_places=2)
    depth = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.date} {self.time} - ({self.latitude}, {self.longitude}) - {self.magnitude}"

class EarthquakeIntensity(models.Model):
    earthquake = models.ForeignKey("Earthquake", on_delete=models.CASCADE, db_constraint=False)
    intensity = models.TextField(max_length=3)
    administrative_area_level_1 = models.TextField(max_length=10)

    def __str__(self):
        return f"{self.administrative_area_level_1} - {self.intensity}"

class CarAccident(models.Model):
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    fatality = models.IntegerField()
    injure = models.IntegerField()
    administrative_area_level_1 = models.TextField(max_length=20)
    administrative_area_level_1 = models.TextField(max_length=20)

    def __str__(self):
        return f"({self.latitude}, {self.longitude}) Fatality: {self.fatality}, Injure: {self.injure}"

class CarAccidentDensity(models.Model):
    latitude_range = models.DecimalField(max_digits=8, decimal_places=5)
    longitude_range = models.DecimalField(max_digits=8, decimal_places=5)
    total_fatality = models.IntegerField()
    total_injure = models.IntegerField()

    def __str__(self):
        return f"({self.latitude_range}, {self.longitude_range}) Total Fatality: {self.total_fatality}, Total Injure: {self.total_injure}"

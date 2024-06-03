from django.db import models


class Earthquake(models.Model):
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    magnitude = models.DecimalField(max_digits=5, decimal_places=2)
    depth = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = "risk_earthquake"

    def __str__(self):
        return f"{self.date} {self.time} - Magnitude: {self.magnitude} in ({self.latitude}, {self.longitude})"

class EarthquakeIntensity(models.Model):
    area = models.TextField(max_length=5)
    number = models.IntegerField()
    intensity = models.TextField(max_length=3)
    pgv_lower = models.DecimalField(max_digits=8, decimal_places=5)

    class Meta:
        db_table = "risk_earthquake_intensity"

    def __str__(self):
        return f"{self.area} - Average Intensity: {self.intensity}"

class CarAccident(models.Model):
    date = models.DateField()
    time = models.TimeField()
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    fatality = models.IntegerField()
    injury = models.IntegerField()
    area_1 = models.TextField(max_length=10)
    area_2 = models.TextField(max_length=10)

    class Meta:
        db_table = "risk_car_accident"

    def __str__(self):
        return f"({self.latitude}, {self.longitude}) Fatality: {self.fatality}, Injure: {self.injury}"

class CarAccidentDensity(models.Model):
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    total_fatality = models.IntegerField()
    total_injury = models.IntegerField()

    class Meta:
        db_table = "risk_car_accident_density"

    def __str__(self):
        return f"({self.latitude}, {self.longitude}) Total Fatality: {self.total_fatality}, Total Injure: {self.total_injury}"

class TrafficAccident(models.Model):
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    number = models.IntegerField()
    total_fatality = models.IntegerField()
    total_injury = models.IntegerField()
    pedestrian_fatality = models.IntegerField()
    pedestrian_injury = models.IntegerField()

    class Meta:
        db_table = "risk_traffic_accident"

    def __str__(self):
        return f"""Traffic Accident in ({self.latitude}, {self.longitude}) -
                    Total Fatality: {self.total_fatality},
                    Total Injure: {self.total_injury}"""

class PedestrianHell(models.Model):
    area_1 = models.TextField(max_length=5)
    area_2 = models.TextField(max_length=10)
    number = models.IntegerField()
    total_fatality = models.IntegerField()
    total_injury = models.IntegerField()
    pedestrian_fatality = models.IntegerField()
    pedestrian_injury = models.IntegerField()

    class Meta:
        db_table = "risk_pedestrian_hell"

    def __str__(self):
        return f"""{self.area_1} {self.area_2} -
                    Pedestrian Fatality: {self.pedestrian_fatality},
                    Pedestrian Total Injure: {self.pedestrian_injury}"""

class UserInfo(models.Model):
    username = models.CharField(max_length=50)
    fullname = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    verification_code = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "user_info"
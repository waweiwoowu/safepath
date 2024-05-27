import os
import sys
import django
import math
from pathlib import Path
from asgiref.sync import sync_to_async
import asyncio
import nest_asyncio
import json

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Construct the project path relative to this script
current_dir = Path(__file__).resolve().parent
project_path = current_dir.parent

# Add the project path to the Python path
sys.path.append(str(project_path))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safepath.settings')

# Initialize Django
django.setup()

# Now import the Django models
from explorer.models import CarAccident, CarAccidentDensity

DEGREE_DIFFERENCE = 0.01

def rounding(degree):
    power = math.log10(DEGREE_DIFFERENCE)
    if power > 0:
        decimal_place = 0
    else:
        decimal_place = math.ceil(abs(power))
    return round(round(float(degree) / DEGREE_DIFFERENCE) * DEGREE_DIFFERENCE, decimal_place)

class Coordinate:
    def __init__(self, latitude=0, longitude=0) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_rounding = rounding(self.latitude)
        self.longitude_rounding = rounding(self.longitude)

    @property
    def is_existing(self):
        pass

class CarAccidentModel():
    def __init__(self):
        self.model = CarAccident()
        # self.names = [field.name for field in self.model._meta.get_fields()]
        
    # Define an async function to fetch Model data
    async def fetch_all(self):
        fetch_data = await sync_to_async(lambda: list(CarAccident.objects.all()))()
        return fetch_data
    
    async def fetch_start_from(self, starting_id):
        fetch_data = await sync_to_async(lambda: list(CarAccident.objects.filter(id__gte=starting_id)))()
        return fetch_data
    
    async def last_data_id(self):
        last_instance = await sync_to_async(lambda: CarAccident.objects.latest("id"))()
        return last_instance.id
    

class CarAccidentDensityModel():
    def __init__(self):
        # self.model = CarAccidentDensity()
        # self.names = [field.name for field in self.model._meta.get_fields()]
        pass
    
    async def create(self, latitude, longitude, fatality, injury):
        is_existing = await sync_to_async(lambda: CarAccidentDensity.objects.filter(latitude=latitude, longitude=longitude).exists())()
        if not is_existing:
            await sync_to_async(lambda: CarAccidentDensity.objects.create(
                latitude=latitude, longitude=longitude, total_fatality=fatality, total_injure=injury))()
        else:
            instance = await sync_to_async(lambda: CarAccidentDensity.objects.get(latitude=latitude, longitude=longitude))()
            instance.total_fatality += fatality
            instance.total_injure += injury
            await sync_to_async(lambda: instance.save())()

async def create_car_accident_density_data(count=1000):
    COUNT = count
    count = 0
    file_path = r".\data\tracking.json"
    with open(file_path) as file:
        tracking = json.load(file)
    accident = CarAccidentModel()
    data = await accident.fetch_start_from(tracking["car_accident_density"]["car_accident_fetching_last_id"]+1)
    for element in data:
        coord = Coordinate(element.latitude, element.longitude)
        density_model = CarAccidentDensityModel()
        await density_model.create(latitude=coord.latitude_rounding, longitude=coord.longitude_rounding, 
                            fatality=element.fatality, injury=element.injury)
        tracking["car_accident_density"]["car_accident_fetching_last_id"] = element.id
        with open(file_path, "w") as file:
            json.dump(tracking, file)
        count += 1
        print(count)
        if count == COUNT:
            break

async def main():
    # coord = Coordinate(25.2525, 123.456)
    # print(coord.latitude_rounding)
    # print(coord.longitude_rounding)
    await create_car_accident_density_data(10000)

    
if __name__ == "__main__":
    asyncio.run(main())

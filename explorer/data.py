import os
import sys
import django
import math
from pathlib import Path
from asgiref.sync import sync_to_async
import asyncio
import nest_asyncio
import json
import aiofiles  # Asynchronous file I/O

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


DEGREE_DIFFERENCE = 0.001
BATCH_SIZE = 100  # Define batch size for fetching records

def rounding(degree, difference=DEGREE_DIFFERENCE):
    power = math.log10(difference)
    if power > 0:
        return round(float(degree) / difference) * difference
    else:
        decimal_place = math.ceil(abs(power))
        return round(round(float(degree) / difference) * difference, decimal_place)

class InvalidCoordinateError(Exception):
    def __init__(self, message="Invalid coordinate. Must provide either a single iterable or separate latitude and longitude values."):
        self.message = message
        super().__init__(self.message)

class Coordinate:
    def __init__(self, *coordinate) -> None:
        """This class is mainly used to determine the round of the coordinate in specific degree difference
        Both Coordinate(25.2525, 123.456) and Coordinate((25.2525, 123.456)) are available"""
        if len(coordinate) == 1:
            if len(coordinate[0]) != 2:
                raise InvalidCoordinateError("Invalid coordinate format. Must provide latitude and longitude values.")
            self.latitude = coordinate[0][0]
            self.longitude = coordinate[0][1]
        elif len(coordinate) == 2:
            self.latitude = coordinate[0]
            self.longitude = coordinate[1]
        else:
            raise InvalidCoordinateError()
            
        if abs(self.latitude) > 90:
            raise InvalidCoordinateError("Invalid latitude value. Must between -90 and 90 degrees.")
        if abs(self.longitude) > 180:
            raise InvalidCoordinateError("Invalid latitude value. Must between -180 and 180 degrees.")
        
        self.latitude_rounding = rounding(self.latitude)
        self.longitude_rounding = rounding(self.longitude)

class CarAccidentModel:
    # Define an async function to fetch Model data
    async def fetch_start_from(self, starting_id, batch_size):
        fetch_data = await sync_to_async(lambda: list(CarAccident.objects.filter(id__gte=starting_id)[:batch_size]))()
        return fetch_data

    async def last_data_id(self):
        last_instance = await sync_to_async(lambda: CarAccident.objects.latest("id"))()
        return last_instance.id

class CarAccidentDensityModel:
    async def create_or_update(self, latitude, longitude, fatality, injury):
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
    file_path = r".\data\tracking.json"
    
    async with aiofiles.open(file_path, mode='r') as file:
        tracking = json.loads(await file.read())
    
    accident = CarAccidentModel()
    last_id = tracking["car_accident_density"]["car_accident_fetching_last_id"] + 1
    processed_count = 0

    while processed_count < count:
        data = await accident.fetch_start_from(last_id, BATCH_SIZE)
        if not data:
            break
        
        density_model = CarAccidentDensityModel()
        tasks = []
        for element in data:
            coord = Coordinate(element.latitude, element.longitude)
            tasks.append(density_model.create_or_update(
                latitude=coord.latitude_rounding, 
                longitude=coord.longitude_rounding, 
                fatality=element.fatality, 
                injury=element.injury
            ))
            last_id = element.id
            processed_count += 1
            if processed_count >= count:
                break

        await asyncio.gather(*tasks)
        
        tracking["car_accident_density"]["car_accident_fetching_last_id"] = last_id
        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(json.dumps(tracking))

async def main():
    coord = Coordinate(25.2525, 123.456)
    print(coord.latitude_rounding)
    print(coord.longitude_rounding)
    # await create_car_accident_density_data(10000)

if __name__ == "__main__":
    asyncio.run(main())

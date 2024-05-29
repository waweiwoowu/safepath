import os
import sys
import django
from pathlib import Path
from asgiref.sync import sync_to_async
import asyncio
import nest_asyncio
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
from explorer.models import CarAccident, CarAccidentDensity, Earthquake
import json
import math


DEGREE_DIFFERENCE = 0.001

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

def casualty(latitude_grid, longitude_grid):
    density = CarAccidentDensityModel()
    data = sync_to_async(lambda: density.fetch(latitude_grid, longitude_grid))()
    # print(data.fatality)
    return (data.fatality, data.injury)

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

        self.latitude_grid = rounding(self.latitude)
        self.longitude_grid = rounding(self.longitude)
        self.car_accident_data = None
        self.earthquake = EarthquakeData(self.latitude, self.longitude)
    
    @property
    async def casualty(self):
        if not self.car_accident_data:
            self.car_accident_data = await sync_to_async(lambda: list(CarAccidentDensity.objects.filter(latitude=self.latitude_grid, longitude=self.longitude_grid)))()
        return (self.car_accident_data[0].total_fatality, self.car_accident_data[0].total_injury)
    
    @property
    async def fatality(self):
        if not self.car_accident_data:
            self.car_accident_data = await sync_to_async(lambda: list(CarAccidentDensity.objects.filter(latitude=self.latitude_grid, longitude=self.longitude_grid)))()
        if len(self.car_accident_data) == 0:
            return 0
        else:
            return self.car_accident_data[0].total_fatality
    
    @property
    async def injury(self):
        if not self.car_accident_data:
            self.car_accident_data = await sync_to_async(lambda: list(CarAccidentDensity.objects.filter(latitude=self.latitude_grid, longitude=self.longitude_grid)))()
        if len(self.car_accident_data) == 0:
            return 0
        else:
            return self.car_accident_data[0].total_injury

class EarthquakeData():
    def __init__(self, latitude, longitude):
        self.latitude = rounding(latitude, 0.01)
        self.longitude = rounding(longitude, 0.01)
        self.data = None

    @property
    async def date(self):
        dates = []
        if not self.data:
            self.data = await sync_to_async(lambda: list(Earthquake.objects.filter(latitude=self.latitude, longitude=self.longitude)))()
        if len(self.data) == 0:
            return None
        else:
            for data in self.data:
                dates.append(data.date)
            return dates
    
    @property
    async def time(self):
        times = []
        if not self.data:
            self.data = await sync_to_async(lambda: list(Earthquake.objects.filter(latitude=self.latitude, longitude=self.longitude)))()
        if len(self.data) == 0:
            return None
        else:
            for data in self.data:
                times.append(data.time)
            return times

    @property
    async def magnitude(self):
        magnitudes = []
        if not self.data:
            self.data = await sync_to_async(lambda: list(Earthquake.objects.filter(latitude=self.latitude, longitude=self.longitude)))()
        if len(self.data) == 0:
            return None
        else:
            for data in self.data:
                magnitudes.append(data.magnitude)
            return magnitudes
    
    @property
    async def depth(self):
        depths = []
        if not self.data:
            self.data = await sync_to_async(lambda: list(Earthquake.objects.filter(latitude=self.latitude, longitude=self.longitude)))()
        if len(self.data) == 0:
            return None
        else:
            for data in self.data:
                depths.append(data.depth)
            return depths

BATCH_SIZE = 100  # Define batch size for fetching records

class CarAccidentModel:
    # Define an async function to fetch Model data
    async def fetch_start_from(self, starting_id, batch_size):
        fetch_data = await sync_to_async(lambda: list(CarAccident.objects.filter(id__gte=starting_id)[:batch_size]))()
        return fetch_data

    async def last_data_id(self):
        last_instance = await sync_to_async(lambda: CarAccident.objects.latest("id"))()
        return last_instance.id

class CarAccidentDensityModel:
    async def fetch(self, latitude, longitude):
        fetch_data = await sync_to_async(lambda: list(CarAccidentDensity.objects.filter(latitude=latitude, longitude=longitude)))()
        return (fetch_data[0].total_fatality, fetch_data[0].total_injury)
    
    async def create_or_update(self, latitude, longitude, fatality, injury):
        obj, created = await sync_to_async(lambda: CarAccidentDensity.objects.get_or_create(
            latitude=latitude, longitude=longitude,
            defaults={'total_fatality': fatality, 'total_injury': injury}
        ))()
        
        if not created:
            obj.total_fatality += fatality
            obj.total_injury += injury
            await sync_to_async(lambda: obj.save())()


async def create_car_accident_density_data(count=100):
    file_path = r".\data\tracking.json"
    
    async with aiofiles.open(file_path, mode='r') as file:
        tracking = json.loads(await file.read())
    
    accident = CarAccidentModel()
    last_id = tracking["car_accident_density"]["car_accident_fetching_last_id"] + 1
    processed_count = 0

    while processed_count < count:
        data = await accident.fetch_start_from(last_id + 1, BATCH_SIZE)
        if not data:
            break
        
        density_model = CarAccidentDensityModel()
        tasks = []
        for element in data:
            coord = Coordinate(element.latitude, element.longitude)
            tasks.append(density_model.create_or_update(
                latitude=coord.latitude_grid, 
                longitude=coord.longitude_grid, 
                fatality=element.fatality, 
                injury=element.injury
            ))
            last_id = element.id
            print(element.id)
            processed_count += 1
            if processed_count >= count:
                break
            
        await asyncio.gather(*tasks)

        tracking["car_accident_density"]["car_accident_fetching_last_id"] = last_id
        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(json.dumps(tracking))


async def main():
    # await create_car_accident_density_data(25000)
    coord = Coordinate(23.6, 120.68)
    print(coord.earthquake.data)
    print(coord.earthquake.latitude)
    print(coord.earthquake.longitude)
    print(await coord.earthquake.date)
    print(await coord.earthquake.time)
    print(await coord.earthquake.magnitude)
    print(await coord.earthquake.depth)
    print(coord.earthquake.data)

if __name__ == "__main__":
    asyncio.run(main())

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
from explorer.models import CarAccident, CarAccidentDensity
from maps import Coordinate
import json


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
    async def create_or_update(self, latitude, longitude, fatality, injury):
        obj, created = await sync_to_async(lambda: CarAccidentDensity.objects.get_or_create(
            latitude=latitude, longitude=longitude,
            defaults={'total_fatality': fatality, 'total_injure': injury}
        ))()
        
        if not created:
            obj.total_fatality += fatality
            obj.total_injure += injury
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
        print("finish tasks")
        tracking["car_accident_density"]["car_accident_fetching_last_id"] = last_id
        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(json.dumps(tracking))
        print("finish writing")

async def main():
    await create_car_accident_density_data(25000)

if __name__ == "__main__":
    asyncio.run(main())

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
from database import CarAccidentModel, CarAccidentDensityModel
from maps import Coordinate, Direction


BATCH_SIZE = 100  # Define batch size for fetching records

async def create_car_accident_density_data(count=1000):
    
    
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
        


async def main():
    direction = await sync_to_async(lambda: Direction())()
    a_to_b = direction.coordinates[:2]
    print(a_to_b)

if __name__ == "__main__":
    asyncio.run(main())

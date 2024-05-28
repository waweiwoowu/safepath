import googlemaps
import math
import asyncio
from constants import API_KEY, TestData
from database import CarAccidentDensityModel


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
        
        self.fatality = self.casualty[0]
        self.injury = self.casualty[1]
    
    @property
    async def casualty(self):
        if not self.data:
            density = CarAccidentDensityModel()
            self.data = await density.fetch(self.latitude_grid, self.longitude_grid)
        return self.data

class Coordinates():
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.grid = []
        for coordinate in coordinates:
            coord = Coordinate(coordinate)
            self.grid.append((coord.latitude_grid, coord.longitude_grid))
        self.grid = list(set(self.grid))

class GoogleMap():
    gmaps = googlemaps.Client(key=API_KEY)

class Geocode(GoogleMap):
    def __init__(self, address=None):
        if not address:
            self.data = TestData.GEOCODE[0]
        else:
            self.data = self.gmaps.geocode(address)[0]
        self.postal_code = self.data["address_components"][-1]["long_name"]
        self.country = self.data["address_components"][-2]["long_name"]
        self.city = self.data["address_components"][-3]["long_name"]
        self.district = self.data["address_components"][-4]["long_name"]
        self.address = self.data["formatted_address"]

    @property
    def location(self):
        self.lat = self.data["geometry"]["location"]["lat"]
        self.lng = self.data["geometry"]["location"]["lng"]
        return (self.lat, self.lng)


class Direction(GoogleMap):
    def __init__(self, origin=None, destination=None):
        if not origin or not destination:
            self.data = TestData.DIRECTIONS[0]
        else:
            self.data = self.gmaps.directions(origin, destination)[0]

    @property
    def overivew_coordinates(self):
        decoded_polyline = googlemaps.convert.decode_polyline(self.data['overview_polyline']['points'])
        route_coordinates = [(point['lat'], point['lng']) for point in decoded_polyline]
        return route_coordinates

    @property
    def coordinates(self):
        route_coordinates = []
        for step in self.data['legs'][0]['steps']:
            polyline = step['polyline']['points']
            decoded_polyline = googlemaps.convert.decode_polyline(polyline)
            route_coordinates += [(point['lat'], point['lng']) for point in decoded_polyline]
        return route_coordinates

    @property
    def fatality(self):
        

async def main():
    # geocode = Geocode()
    # print(geocode.data)
    # print(geocode.city)
    # print(geocode.district)
    # print(geocode.address)
    # print(geocode.location)

    direction = Direction()
    # print(direction.overivew_coordinates)
    print(len(direction.coordinates))

    # coord = Coordinate(25.2525, 123.456)
    # print(coord.latitude_grid)
    # print(coord.longitude_grid)
    
    coords = Coordinates(direction.coordinates)
    print(coords.grid)

    direction = Direction()
    data = await get_density((25.0017, 121.5806))
    print(data)


if __name__ == "__main__":
    asyncio.run(main())


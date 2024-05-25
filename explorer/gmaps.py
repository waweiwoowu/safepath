import googlemaps
from constants import API_KEY, TestData


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


if __name__ == "__main__":
    geocode = Geocode()
    print(geocode.data)
    print(geocode.city)
    print(geocode.district)
    print(geocode.address)
    print(geocode.location)

    direction = Direction()
    print(direction.overivew_coordinates)
    print(direction.coordinates)
    
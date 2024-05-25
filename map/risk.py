from models import CarAccident, CarAccidentDensity


LATITUDE_DIFFERENCE = 0.01
LONGITUDE_DIFFERENCE = 0.01

class Coordinate():
    def __init__(self, latitude=0, longitude=0) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_range = round(self.latitude / LATITUDE_DIFFERENCE)

if __name__ == "__main__":
    coord = Coordinate(25.2525, 123.456)
    print(coord.latitude_range)


import math


DEGREE_DIFFERENCE = 0.01

def rounding(degree):
    power = math.log10(DEGREE_DIFFERENCE)
    if power > 0:
        decimal_place = 0
    else:
        decimal_place = math.ceil(abs(power))
    return round(round(degree / DEGREE_DIFFERENCE) * DEGREE_DIFFERENCE, decimal_place)

class Coordinate:
    def __init__(self, latitude=0, longitude=0) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_rounding = rounding(self.latitude)
        self.longitude_rounding = rounding(self.longitude)

    @property
    def is_existing(self):
        pass


if __name__ == "__main__":
    coord = Coordinate(25.2525, 123.456)
    print(coord.latitude_rounding)
    print(coord.longitude_rounding)

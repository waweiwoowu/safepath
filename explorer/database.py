import json
import math
import sqlite3
import pandas as pd
from datetime import datetime


DEGREE_DIFFERENCE = 0.0001

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
        self.car_accident_data = None
        # self.earthquake = EarthquakeData(self.latitude, self.longitude)

class InvalidCarAccidentError(Exception):
    def __init__(self, message="Invalid."):
        self.message = message
        super().__init__(self.message)

class CarAccident:
    """This class is used to read data from car accident csv files."""
    def __init__(self, year, month=None, rank=2):
        self.year = year
        self.month = month
        self.rank = rank
        self._is_arg_valid()
        self.df = pd.DataFrame()
        self._read_csv_file()
        self.get = GetCarAccidentData(self.df)

    def _is_arg_valid(self):

        path = r".\data\tracking.json"
        with open(path) as file:
            data = json.load(file)
            starting_year = data["car_accident"]["starting_year"]
            ending_year = data["car_accident"]["ending_year"]
        if (type(self.year) != int or (self.year < starting_year or self.year > ending_year)):
            raise InvalidCarAccidentError(f"Invalid year. Must be an integer between {starting_year} and {ending_year} (including).")
        if self.month:
            if type(self.month) != int or (self.month < 1 or self.month > 12):
                raise InvalidCarAccidentError("Invalid mouth. Must be an integer between 1 and 12 (including).")

    def _read_csv_file(self):
        dtype_mapping = {
            '發生日期': str,
            '發生時間': str,
            '經度': float,
            '緯度': float,
            '死亡受傷人數': str,
            '發生地點': str
        }
        if self.rank == 1 or self.rank == '1' or self.rank == "A1" or self.rank == "a1":
            self.df = pd.read_csv(f"./data/accidents/{self.year}/{self.year}年度A1交通事故資料.csv")
            self.df = self.df[:-2]
            if self.month:
                self.df['發生日期'] = self.df['發生日期'].astype(int)
                if self.month > 9:
                    self.df = self.df[self.df['發生日期'].astype(str).str[4:6] == str(self.month)]
                else:
                    self.df = self.df[self.df['發生日期'].astype(str).str[4:6] == f"0{self.month}"]
                self.df['發生日期'] = self.df['發生日期'].astype(float)
                self.df = self.df.reset_index(drop=True)
        elif self.rank == 2 or self.rank == '2' or self.rank == "A2" or self.rank == "a2":
            if not self.month:
                for m in range(1, 13):
                    monthly_data = pd.read_csv(f"./data/accidents/{self.year}/{self.year}年度A2交通事故資料_{m}.csv", dtype=dtype_mapping, low_memory=False)
                    monthly_data = monthly_data[:-2]
                    self.df = pd.concat([self.df, monthly_data], ignore_index=True)
            else:
                self.df = pd.read_csv(f"./data/accidents/{self.year}/{self.year}年度A2交通事故資料_{self.month}.csv", dtype=dtype_mapping, low_memory=False)
                self.df = self.df[:-2]
        else:
            raise InvalidCarAccidentError("Invalid rank. Must be either 1, '1', 'A1', 'a1', or 2, '2', 'A2', 'a2'.")

class GetCarAccidentData:
    def __init__(self, df):
        self.df = df
        self._dates = [datetime.strptime(str(int(d)), '%Y%m%d').strftime('%Y-%m-%d') for d in self.df['發生日期']]
        self._times = [datetime.strptime(str(int(t)).zfill(6), '%H%M%S').strftime('%H:%M:%S') for t in self.df['發生時間']]
        self._longitudes = self.df['經度']
        self._latitudes = self.df['緯度']
        self._casualties = self.df['死亡受傷人數']
        self._fatalities = [int(c[2]) for c in self._casualties]
        self._injuries = [int(c[-1]) for c in self._casualties]
        self._location = self.df['發生地點']
        self._administrative_area_level_1 = [loc[:3] for loc in self._location]
        self._administrative_area_level_2 = [loc[3:6] for loc in self._location]
        self._reorganize_data()

    def _reorganize_data(self):
        check = 0
        longitude_check = 0
        latitude_check = 0
        self._data = []
        for i in range(len(self._dates)):
            if self._times[i] == check:
                if (self._longitudes[i] == longitude_check) and (self._latitudes[i] == latitude_check):
                    continue
                else:
                    longitude_check = self._longitudes[i]
                    latitude_check = self._latitudes[i]
            else:
                check = self._times[i]
                self._data.append([
                    self._dates[i],
                    self._times[i],
                    self._latitudes[i],
                    self._longitudes[i],
                    self._fatalities[i],
                    self._injuries[i],
                    self._administrative_area_level_1[i],
                    self._administrative_area_level_2[i]
                ])
        self._newdata = pd.DataFrame(self._data, columns=[
            'date',
            'time',
            'latitude',
            'longitude',
            'fatality',
            'injury',
            'administrative_area_level_1',
            'administrative_area_level_2'
        ])
        self._dates = self._newdata.iloc[:, 0]
        self._times = self._newdata.iloc[:, 1]
        self._latitudes = self._newdata.iloc[:, 2]
        self._longitudes = self._newdata.iloc[:, 3]
        self._fatalities = self._newdata.iloc[:, 4]
        self._injuries = self._newdata.iloc[:, 5]
        self._administrative_area_level_1s = self._newdata.iloc[:, 6]
        self._administrative_area_level_2s = self._newdata.iloc[:, 7]

    def date(self, id=None):
        if id:
            return self._dates[id-1]
        else:
            return self._dates

    def time(self, id=None):
        if id:
            return self._times[id-1]
        else:
            return self._times

    def latitude(self, id=None):
        if id:
            return self._latitudes[id - 1]
        else:
            return self._latitudes

    def longitude(self, id=None):
        if id:
            return self._longitudes[id-1]
        else:
            return self._longitudes

    def fatality(self, id=None):
        if id:
            return self._fatalities[id-1]
        else:
            return self._fatalities

    def injury(self, id=None):
        if id:
            return self._injuries[id-1]
        else:
            return self._injuries

    def administrative_area_level_1(self, id=None):
        if id:
            return self._administrative_area_level_1s[id-1]
        else:
            return self._administrative_area_level_1s

    def administrative_area_level_2(self, id=None):
        if id:
            return self._administrative_area_level_2s[id-1]
        else:
            return self._administrative_area_level_2s

class AllCarAccidentData:
    def __init__(self, rank=2):
        self._get_years()
        self._rank = rank
        self._get_data()
        
    def _get_years(self):
        path = r".\data\tracking.json"
        with open(path) as file:
            data = json.load(file)
            self._starting_year = data["car_accident"]["starting_year"]
            self._ending_year = data["car_accident"]["ending_year"]
            
    def _get_data(self):
        for year in range(self._starting_year, self._ending_year + 1):
            for month in range(1, 13):
                accident = CarAccident(year=year, month=month, rank=self._rank)


                
class SQLController:
    PATH = r"..\.\db.sqlite3"
    def __init__(self):
        self.conn = sqlite3.connect(SQLController.PATH)
        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def select(self, id=None):
        if id:
            sql = f"SELECT * FROM risk_car_accident_density where id={id}"
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        else:
            sql = "SELECT * FROM risk_car_accident_density"
            self.cursor.execute(sql)
            return self.cursor.fetchall()     

class CarAccdentDensitySQLController(SQLController):
    def __init__(self):
        self.conn = sqlite3.connect(SQLController.PATH)
        self.cursor = self.conn.cursor()

    def new(self, latitude, longitude, fatality, injury):
        coordinate = Coordinate(latitude, longitude)
        self.existing_id = self.coordinate_id(coordinate.latitude_grid, coordinate.longitude)
        if self.existing_id:
            sql = f"UPDATE risk_car_accident_density SET total_fatality = {fatality}, total_injury = {injury} WHERE id = '{self.existing_id}'"
            self.cursor.execute(sql)
        else:
            sql = "INSERT INTO risk_car_accident_density (latitude, longitude, total_fatality, total_injury) VALUES (?, ?, ?, ?)"
            self.cursor.execute(sql, (coordinate.latitude, coordinate.longitude, fatality, injury))
        self.conn.commit()
    
    def coordinate_id(self, latitude, longitude):
        sql = f"SELECT * FROM risk_car_accident_density where latitude={latitude} and longitude={longitude}"
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None


def test_CarAccident():
    accident = CarAccident(year=111, month=12, rank=2)
    print(accident.get.date())
    print(accident.get.time())
    print(accident.get.latitude())
    print(accident.get.longitude())
    print(accident.get.fatality())
    print(accident.get.injury())
    print(accident.get.administrative_area_level_1())
    print(accident.get.administrative_area_level_2())
    data_id = 1
    print(accident.get.date(data_id))
    print(accident.get.time(data_id))
    print(accident.get.latitude(data_id))
    print(accident.get.longitude(data_id))
    print(accident.get.fatality(data_id))
    print(accident.get.injury(data_id))
    print(accident.get.administrative_area_level_1(data_id))
    print(accident.get.administrative_area_level_2(data_id))

def test_SQLController():
    controller = CarAccdentDensitySQLController()
    test_latitude = 24.4389
    test_longitude = 118.2497
    # print(controller.coordinate_id(test_latitude, test_longitude))
    # print(controller.coordinate_id(test_latitude+50, test_longitude))
    print(controller.select(50956))
    controller.new(test_latitude, test_longitude, 55, 66)
    print(controller.select(50956))
    controller.new(test_latitude, test_longitude, 99, 77)
    print(controller.select(50956))
    controller.new(test_latitude+50, test_longitude+20, 55, 123)
    controller.close()


if __name__ == "__main__":
    # test_CarAccident()
    test_SQLController()


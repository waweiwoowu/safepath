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
        self._year = year
        self._month = month
        self._rank = rank
        self._is_arg_valid()
        self._df = pd.DataFrame()
        self._read_csv_file()
        self._get_data()

    def _is_arg_valid(self):
        path = r".\data\tracking.json"
        with open(path) as file:
            data = json.load(file)
            starting_year = data["car_accident"]["starting_year"]
            ending_year = data["car_accident"]["ending_year"]
        if (type(self._year) != int or (self._year < starting_year or self._year > ending_year)):
            raise InvalidCarAccidentError(f"Invalid year. Must be an integer between {starting_year} and {ending_year} (including).")
        if self._month:
            if type(self._month) != int or (self._month < 1 or self._month > 12):
                raise InvalidCarAccidentError("Invalid mouth. Must be an integer between 1 and 12 (including).")

    def _read_csv_file(self):
        dtype_mapping = {
            "發生日期": str,
            "發生時間": str,
            "經度": float,
            "緯度": float,
            "死亡受傷人數": str,
            "發生地點": str,
            "事故類型": str
        }
        if self._rank == 1 or self._rank == '1' or self._rank == "A1" or self._rank == "a1":
            self._df = pd.read_csv(f"./data/accidents/{self._year}/{self._year}年度A1交通事故資料.csv")
            self._df = self._df[:-2]
            # if self._month:
            #     self._df['發生日期'] = self._df['發生日期'].astype(int)
            #     if self._month > 9:
            #         self._df = self._df[self._df['發生日期'].astype(str).str[4:6] == str(self._month)]
            #     else:
            #         self._df = self._df[self._df['發生日期'].astype(str).str[4:6] == f"0{self._month}"]
            #     self._df['發生日期'] = self._df['發生日期'].astype(float)
            #     self._df = self._df.reset_index(drop=True)
        elif self._rank == 2 or self._rank == '2' or self._rank == "A2" or self._rank == "a2":
            if not self._month:
                for m in range(1, 13):
                    monthly_data = pd.read_csv(f"./data/accidents/{self._year}/{self._year}年度A2交通事故資料_{m}.csv", dtype=dtype_mapping, low_memory=False)
                    monthly_data = monthly_data[:-2]
                    self._df = pd.concat([self._df, monthly_data], ignore_index=True)
            else:
                self._df = pd.read_csv(f"./data/accidents/{self._year}/{self._year}年度A2交通事故資料_{self._month}.csv", dtype=dtype_mapping, low_memory=False)
                self._df = self._df[:-2]
        else:
            raise InvalidCarAccidentError("Invalid rank. Must be either 1, '1', 'A1', 'a1', or 2, '2', 'A2', 'a2'.")

    def _get_data(self):
        self._dates = [datetime.strptime(str(int(d)), "%Y%m%d").strftime("%Y-%m-%d") for d in self._df["發生日期"]]
        self._times = [datetime.strptime(str(int(t)).zfill(6), "%H%M%S").strftime("%H:%M:%S") for t in self._df["發生時間"]]
        self._longitudes = self._df["經度"]
        self._latitudes = self._df["緯度"]
        self._casualties = self._df["死亡受傷人數"]
        self._fatalities = [int(c[2]) for c in self._casualties]
        self._injuries = [int(c[-1]) for c in self._casualties]
        self._location = self._df["發生地點"]
        self._administrative_area_level_1 = [loc[:3] for loc in self._location]
        self._administrative_area_level_2 = [loc[3:6] for loc in self._location]
        self._includes_pedestrian = self._df["事故類型及型態大類別名稱"].str.contains('人')
        
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
                    self._administrative_area_level_2[i],
                    self._includes_pedestrian[i]
                ])
        self.data = pd.DataFrame(self._data, columns=[
            "date",
            "time",
            "latitude",
            "longitude",
            "fatality",
            "injury",
            "administrative_area_level_1",
            "administrative_area_level_2",
            "includes_pedestrian"
        ])
        self._dates = self.data.iloc[:, 0]
        self._times = self.data.iloc[:, 1]
        self._latitudes = self.data.iloc[:, 2]
        self._longitudes = self.data.iloc[:, 3]
        self._fatalities = self.data.iloc[:, 4]
        self._injuries = self.data.iloc[:, 5]
        self._administrative_area_level_1s = self.data.iloc[:, 6]
        self._administrative_area_level_2s = self.data.iloc[:, 7]
        self._includes_pedestrian = self.data.iloc[:, 8]

    def date(self, id=None):
        if id is not None:
            return self._dates[id]
        else:
            return self._dates

    def time(self, id=None):
        if id is not None:
            return self._times[id]
        else:
            return self._times

    def latitude(self, id=None):
        if id is not None:
            return self._latitudes[id]
        else:
            return self._latitudes

    def longitude(self, id=None):
        if id is not None:
            return self._longitudes[id]
        else:
            return self._longitudes

    def fatality(self, id=None):
        if id is not None:
            return int(self._fatalities[id])
        else:
            return self._fatalities

    def injury(self, id=None):
        if id is not None:
            return int(self._injuries[id])
        else:
            return self._injuries

    def administrative_area_level_1(self, id=None):
        if id is not None:
            return self._administrative_area_level_1s[id]
        else:
            return self._administrative_area_level_1s

    def administrative_area_level_2(self, id=None):
        if id is not None:
            return self._administrative_area_level_2s[id]
        else:
            return self._administrative_area_level_2s
    
    def includes_pedestrian(self, id=None):
        if id is not None:
            return self._includes_pedestrian[id]
        else:
            return self._includes_pedestrian

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
    def __init__(self, table_name):
        self.table_name = table_name
        self.conn = sqlite3.connect(SQLController.PATH)
        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def select(self, id=None, column=None):
        if id:
            if column:
                sql = f"SELECT {column} FROM {self.table_name} where id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()[0]
            else:
                sql = f"SELECT * FROM {self.table_name} where id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()
        else:
            sql = "SELECT * FROM {self.table_name}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

class TrafficAccidentsSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_traffic_accidents"
        super().__init__(self.table_name)

    def new(self, latitude, longitude, fatality, injury):
        coordinate = Coordinate(latitude, longitude)
        self.existing_id = self.coordinate_id(coordinate.latitude_grid, coordinate.longitude_grid)
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            fatality += self.select(self.existing_id, "fatality")
            injury += self.select(self.existing_id, "injury")
            sql = f"UPDATE {self.table_name} SET number = {number}, fatality = {fatality}, injury = {injury} WHERE id = {self.existing_id}"
            self.cursor.execute(sql)
        else:
            sql = f"INSERT INTO {self.table_name} (latitude, longitude, number, fatality, injury) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (coordinate.latitude_grid, coordinate.longitude_grid, 1, fatality, injury))
        self.conn.commit()
    
    def coordinate_id(self, latitude, longitude):
        sql = f"SELECT * FROM {self.table_name} where latitude = {latitude} and longitude = {longitude}"
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class PedestrianHell(SQLController):
    def __init__(self):
        self.table_name = "risk_pedestrian_hell"
        super().__init__(self.table_name)

    def new(self, latitude, longitude, fatality, injury):
        coordinate = Coordinate(latitude, longitude)
        self.existing_id = self.coordinate_id(coordinate.latitude_grid, coordinate.longitude_grid)
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            fatality += self.select(self.existing_id, "fatality")
            injury += self.select(self.existing_id, "injury")
            sql = f"UPDATE {self.table_name} SET number = {number}, fatality = {fatality}, injury = {injury} WHERE id = {self.existing_id}"
            self.cursor.execute(sql)
        else:
            sql = f"INSERT INTO {self.table_name} (latitude, longitude, number, fatality, injury) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (coordinate.latitude_grid, coordinate.longitude_grid, 1, fatality, injury))
        self.conn.commit()
    
    def coordinate_id(self, latitude, longitude):
        sql = f"SELECT * FROM {self.table_name} where latitude = {latitude} and longitude = {longitude}"
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class UpdateTrafficAccidentsData:
    def __init__(self):
        self.get_tracking_data()
        self.update_data()
        
    def get_tracking_data(self):
        path = r".\data\tracking.json"
        with open(path) as file:
            data = json.load(file)
            self.starting_year = data["car_accident"]["starting_year"]
            self.ending_year = data["car_accident"]["ending_year"]
            self.tracking_year = data["car_accident_density"]["tracking_year"]
            self.tracking_month = data["car_accident_density"]["tracking_month"]
            self.tracking_rank = data["car_accident_density"]["tracking_rank"]
    
    def initialize_range(self):
        if not self.tracking_year:
            self.tracking_year = self.starting_year
        if not self.tracking_month:
            self.tracking_month = 0
        if not self.tracking_rank:
            self.tracking_rank = 1
    
    def determine_range(self):
        self.initialize_range()
        if self.tracking_rank == 1:
            if self.tracking_month == 0:
                self.tracking_month = 12
            elif self.tracking_month == 12:
                self.tracking_rank = 2
                self.tracking_month = 0
        if self.tracking_rank == 2:
            if self.tracking_month == 12:
                self.tracking_year += 1
                self.tracking_rank = 1
            else:
                self.tracking_month += 1

    def update_data(self):
        self.determine_range()
        self.accident = CarAccident(year=self.tracking_year, month=self.tracking_month, rank=self.tracking_rank)
        self.traffic_sql_controller = TrafficAccidentsSQLController()
        for i in range(len(self.accident.data)):
            latitude = self.accident.latitude(i)
            longitude = self.accident.longitude(i)
            fatality = self.accident.fatality(i)
            injury = self.accident.injury(i)
            # self.traffic_sql_controller.new(latitude, longitude, fatality, injury)
            break
        
        

def test_CarAccident():
    accident = CarAccident(year=111, month=2, rank=2)
    # print(accident.date())
    # print(accident.time())
    # print(accident.latitude())
    # print(accident.longitude())
    # print(accident.fatality())
    # print(accident.injury())
    # print(accident.administrative_area_level_1())
    # print(accident.administrative_area_level_2())
    print(accident.includes_pedestrian())
    print(accident.includes_pedestrian().sum())
    data_id = 1
    print(accident.date(data_id))
    print(accident.time(data_id))
    print(accident.latitude(data_id))
    print(accident.longitude(data_id))
    print(accident.fatality(data_id))
    print(accident.injury(data_id))
    print(accident.administrative_area_level_1(data_id))
    print(accident.administrative_area_level_2(data_id))

def test_SQLController():
    controller = CarAccdentDensitySQLController()
    test_latitude = 24.4389
    test_longitude = 118.2497
    # print(controller.coordinate_id(test_latitude, test_longitude))
    # print(controller.coordinate_id(test_latitude+50, test_longitude))
    print(controller.select(50956, "total_injury"))
    # controller.new(test_latitude, test_longitude, 55, 66)
    # print(controller.select(50956))
    # controller.new(test_latitude, test_longitude, 99, 77)
    # print(controller.select(50956))
    # controller.new(test_latitude+50, test_longitude+20, 55, 123)
    controller.close()

def test_UpdateTrafficAccidentsData():
    UpdateTrafficAccidentsData()

if __name__ == "__main__":
    # test_CarAccident()
    # test_SQLController()
    test_UpdateTrafficAccidentsData()


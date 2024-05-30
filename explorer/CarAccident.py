import pandas as pd
from datetime import datetime

class CarAccident:
    def __init__(self, year, month=None):
        self.year = year
        self.month = month
        if month:
            self.datas = pd.read_csv(f".\\data\\accidents\\{year}\\{year}年度A2交通事故資料_{month}.csv")
        else:
            self.datas = pd.read_csv(f".\\data\\accidents\\{year}\\{year}年度A1交通事故資料.csv")
        
        self.datas = self.datas[:-2]
        self.dates = [datetime.strptime(str(int(d)), '%Y%m%d').strftime('%Y-%m-%d') for d in self.datas['發生日期']]
        self.times = [datetime.strptime(str(int(t)).zfill(6), '%H%M%S').strftime('%H:%M:%S') for t in self.datas['發生時間']]
        self.longitudes = self.datas['經度']
        self.latitudes = self.datas['緯度']
        self.casualties = self.datas['死亡受傷人數']
        self.fatalities = [int(c[2]) for c in self.casualties]
        self.injuries = [int(c[-1]) for c in self.casualties]
        self.location = self.datas['發生地點']
        self.administrative_area_level_1 = [loc[:3] for loc in self.location]
        self.administrative_area_level_2 = [loc[3:6] for loc in self.location]
        
        check = 0
        longitude_check = 0
        latitude_check = 0
        self.data = []
        for i in range(len(self.dates)):
            if self.times[i] == check:
                if (self.longitudes[i] == longitude_check) and (self.latitudes[i] == latitude_check):
                    continue
                else:
                    longitude_check = self.longitudes[i]
                    latitude_check = self.latitudes[i]
            else:
                check = self.times[i]
                self.data.append([
                    self.dates[i],
                    self.times[i],
                    self.latitudes[i],
                    self.longitudes[i],
                    self.fatalities[i],
                    self.injuries[i],
                    self.administrative_area_level_1[i],
                    self.administrative_area_level_2[i]
                ])
        
        self.newdata = pd.DataFrame(self.data, columns=[
            'date',
            'time',
            'latitude',
            'longitude',
            'fatality',
            'injury',
            'administrative_area_level_1',
            'administrative_area_level_2'
        ])
        
        self.dates = self.newdata.iloc[:, 0]
        self.times = self.newdata.iloc[:, 1]
        self.latitudes = self.newdata.iloc[:, 2]
        self.longitudes = self.newdata.iloc[:, 3]
        self.fatalities = self.newdata.iloc[:, 4]
        self.injuries = self.newdata.iloc[:, 5]
        self.administrative_area_level_1s = self.newdata.iloc[:, 6]
        self.administrative_area_level_2s = self.newdata.iloc[:, 7]

    def get(self):
        return self.newdata
    
    def get_date(self, id):
        return self.dates[id - 1]
    
    def get_time(self, id):
        return self.times[id - 1]
    
    def get_latitude(self, id):
        return self.latitudes[id - 1]
    
    def get_longitude(self, id):
        return self.longitudes[id - 1]
    
    def get_fatality(self, id):
        return self.fatalities[id - 1]
    
    def get_injury(self, id):
        return self.injuries[id - 1]
    
    def get_administrative_area_level_1(self, id):
        return self.administrative_area_level_1s[id - 1]
    
    def get_administrative_area_level_2(self, id):
        return self.administrative_area_level_2s[id - 1]

if __name__ == "__main__":
    accident = CarAccident(year=111,month=5)
    # print(accident.get_date(10))
    # print(accident.get_time(10))
    # print(accident.get_latitude(10))
    # print(accident.get_longitude(10))
    # print(accident.get_fatality(10))
    # print(accident.get_injury(10))
    # print(accident.get_administrative_area_level_1(10))
    # print(accident.get_administrative_area_level_2(10))
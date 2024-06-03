# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 14:22:18 2024

@author: 恆慈
"""

import pandas as pd


class earthquake:
    def __init__(self,year):
        self.data = pd.read_csv(f".\data\earthquakes\earthquake_{year}年.csv", engine='python')
        
    
    def date(self,id = None):
        date = self.data["Date"]
        if id is None:
            return date
        else:
            return date[id]

    def time(self,id = None):
        time = self.data["Time"]
        if id is None:
            return time
        else:
            return time[id]
        
    def latitude(self,id = None):
        latitude = self.data["北緯"]
        if id is None:
            return latitude
        else:
            return latitude[id]
        
    def longitude(self,id = None):
        longitude = self.data["東經"]
        if id is None:
            return longitude
        else:
            return longitude[id]
        
    def depth(self,id = None):
        depth = self.data["深度"]
        if id is None:
            return depth
        else:
            return depth[id]
        
    def magnitude(self,id = None):
        magnitude = self.data["芮氏規模"]
        if id is None:
            return magnitude
        else:
            return magnitude[id]
        
    def area(self,id = None):
        area = self.data["城市"]
        if id is None:
            return area
        else:
            return area[id]

    def intensity(self,id = None):
        intensity = self.data["震度"]
        if id is None:
            return intensity
        else:
            return intensity[id]+"級"
        

if __name__ == "__main__":
    year = eval(input("查詢年份:"))
    eq = earthquake(year)
    in_id = eval(input("查詢ID:"))
    print(eq.date(in_id))
    print(eq.time(in_id))
    print(eq.latitude(in_id))
    print(eq.longitude(in_id))
    print(eq.depth(in_id))
    print(eq.magnitude(in_id))
    print(eq.area(in_id))
    print(eq.intensity(in_id))
    
import sqlite3
import pandas as pd

# 讀取 CSV 檔案
starting_year = 110
year = 113
df = pd.read_csv(f".\\data\\accidents\\{year}年度A2交通事故資料_{month}.csv")

# 連接到 SQLite 資料庫
conn = sqlite3.connect(r'..\db.sqlite3')

# 創建一個 cursor 物件
cursor = conn.cursor()

# 插入資料到 CarAccident 表
for index, row in df.iterrows():
    cursor.execute('''INSERT INTO risk_car_accident (date, time, latitude, longitude, fatality, injury, administrative_area_level_1, administrative_area_level_2)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (row['date'], row['time'], row['latitude'], row['longitude'], row['fatality'], row['injury'], row['administrative_area_level_1'], row['administrative_area_level_2']))

# 提交事務
conn.commit()

# 關閉連接
conn.close()

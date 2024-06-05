import pandas as pd

# 讀取 CSV 文件
df = pd.read_csv("Taiwan_attractions_3.csv")

# 新增 'image' 欄位，並且將 'title' 欄位的值前面加上 'HotSpot_pic\'
df['image'] = r'HotSpot_pic/' + df['title']+".jpg"


# 顯示結果
print(df.head())

# 顯示結果
print(df.head())

df.to_csv("Taiwan_attractions_3_updated.csv",encoding="utf-8-sig", index=False)

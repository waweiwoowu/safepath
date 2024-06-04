import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO

# 設置 Chrome 選項，使瀏覽器啟動時不顯示視窗
chrome_options = Options()
chrome_options.add_argument('--headless')  # 啟用 headless 模式
driver = webdriver.Chrome(options=chrome_options)

# 創建資料夾以保存圖片
img_dir = r'.././static/images/hotspots/taiwan_img'
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

# 初始化一個空的 DataFrame
columns = ['title', 'image', 'area_1', 'area_2', 'latitude', 'longitude']
df = pd.DataFrame(columns=columns)

# 爬蟲邏輯
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
url = "https://www.taiwan.net.tw/m1.aspx?sNo=0000501"
r = requests.get(url, headers=headers)
if r.status_code == requests.codes.ok:
    soup = BeautifulSoup(r.text, "html.parser")
    href = soup.find_all('a', class_='circularbtn')

for h in range(len(href)):
    url2 = "https://www.taiwan.net.tw/" + href[h].get('href')
    r = requests.get(url2, headers=headers)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        href2 = soup.find_all('a', class_='card-link')
    
    for h2 in range(len(href2)):
        url3 = "https://www.taiwan.net.tw/" + href2[h2].get('href')
        
        driver.get(url3)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "lazyloaded"))
            )
        except:
            print(f"圖片元素未找到或等待超時：{url3}")
            continue
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find('h2').text.strip()
        pic_url = soup.find('img', class_='lazyloaded').get('data-src')
        address = soup.find('a', class_='tel-link address').text.strip()
        administrative_area_level_1 = address[:3]
        administrative_area_level_2 = address[3:6]

        # 地址长度检查
        if len(administrative_area_level_2) > 2 and administrative_area_level_2[2] not in "鄉鎮市區":
            administrative_area_level_2 = address[3:5]
        
        address2 = soup.find_all('dd')
        latitude = longitude = None
        for a in address2:
            text = a.get_text()
            if "/" in text:
                coords = text.split('/')
                latitude = coords[1]
                longitude = coords[0]
                break  
    
        # 下載並保存圖片
        response = requests.get(pic_url)
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        
        # 替換文件名中的非法字符
        img_filename = f"{title.replace('/', '_').replace(':', '_')}.jpg"
        img_path = os.path.join(img_dir, img_filename)
        img.save(img_path)
    
        # 添加數據到 DataFrame
        df = df.append({
            'title': title,
            'image':f'/hotspots/taiwan_img/{img_filename}',
            'area_1': administrative_area_level_1,
            'area_2': administrative_area_level_2,
            'address': address,
            'latitude': latitude,
            'longitude': longitude
        }, ignore_index=True)

driver.quit()

# 保存 DataFrame 到 CSV 文件
data_dir = './data/hotspots'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

df.to_csv(os.path.join(data_dir, 'data_north.csv'), index=False, encoding='utf-8-sig')
print("數據已保存到 data_north.csv")

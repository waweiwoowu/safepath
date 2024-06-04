import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import googlemaps
import pandas as pd
# 爬蟲 Edited By 肥包子 Jun 2, 2024, 11:13 PM
# 下載圖片
# 存 CSV 欄位為: 景點 地址 經度 緯度 圖片 url 
# 替換為你的 Google Maps API key
API_KEY = 'Your Google Maps API key'

gmaps = googlemaps.Client(key=API_KEY)

def scrape_hotspots(region_url):
    response = requests.get(region_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有具有 class 'sec2' 的 div 元素
        sec2_divs = soup.find_all('div', class_='sec2')
        
        hotspots = []
        
        for sec2 in sec2_divs:
            # 找到 'h2' 標籤並確保標題是包含'熱門景點'
            h2 = sec2.find('h2')
            if h2 and '熱門景點' in h2.text:
                # 找到所有包含景點資訊的 'li' 標籤
                li_tags = sec2.find_all('li', style="height:auto !important;overflow:auto;")
                for li in li_tags:
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        # 提取景點名稱和 URL
                        spot_name = a_tag.find('span', class_='tooltip').text.strip()
                        spot_url = urljoin(region_url, a_tag['href'])
                        hotspots.append((spot_name, spot_url))
                        
        return hotspots
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

def get_place_details(place_name):
    geocode_result = gmaps.geocode(place_name)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        address = geocode_result[0]['formatted_address']
        return address, location['lat'], location['lng']
    return None, None, None

def download_image(image_url, image_name):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(image_name, 'wb') as out_file:
            for chunk in response.iter_content(1024):
                out_file.write(chunk)

def scrape_image_url(spot_url):
    response = requests.get(spot_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        image_div = soup.find('div', id='Buty_Title_Pic')
        if image_div:
            img_tag = image_div.find('img')
            if img_tag and 'src' in img_tag.attrs:
                return img_tag['src']
    return None

# 北部區域的 URL
north_url = 'https://okgo.tw/buty/#tab1'

# 抓取北部區域的熱門景點
north_hotspots = scrape_hotspots(north_url)

# 收集數據
data = []

# 創建圖片資料夾
if not os.path.exists('HotSpot_pic'):
    os.makedirs('HotSpot_pic')

# 使用 Google Maps API 取得地址和經緯度，並下載圖片
for name, url in north_hotspots:
    address, lat, lng = get_place_details(name)
    image_url = scrape_image_url(url)
    if image_url:
        image_name = f"HotSpot_pic/{name}.jpg"
        download_image(image_url, image_name)
        print(f"Downloaded image for {name}")
    if address:
        data.append([name, address, lat, lng, image_url])

# 創建 DataFrame
df = pd.DataFrame(data, columns=['景點', '地址', '經度', '緯度', '圖片URL'])

# 將結果存為 CSV 文件
df.to_csv('north_hotspots.csv', index=False, encoding='utf-8-sig')

print("Data has been saved to addr_lati_longi_picUrl.csv")
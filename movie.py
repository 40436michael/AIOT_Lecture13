import requests
from bs4 import BeautifulSoup
import csv
import time

# -----------------------------
# CSV 檔名
# -----------------------------
output_file = 'movie.csv'

# -----------------------------
# 爬取頁數
# -----------------------------
base_url = "https://ssr1.scrape.center/page/{}"
pages = range(1, 11)  # page 1 ~ page 10

# -----------------------------
# CSV 標題
# -----------------------------
fields = ['電影名稱', '電影圖片 URL', '評分', '類型']

# -----------------------------
# 存 CSV 檔
# -----------------------------
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(fields)

    for page in pages:
        url = base_url.format(page)
        print(f"正在抓取: {url}")
        
        # 發送請求
        response = requests.get(url)
        if response.status_code != 200:
            print(f"無法抓取第 {page} 頁")
            continue
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 每部電影的容器
        movie_items = soup.select('.el-card')
        
        for item in movie_items:
            # 電影名稱
            name_tag = item.select_one('.name')
            name = name_tag.get_text(strip=True) if name_tag else ''
            
            # 電影圖片 URL
            img_tag = item.select_one('img')
            img_url = img_tag['src'] if img_tag else ''
            
            # 評分
            score_tag = item.select_one('.score')
            score = score_tag.get_text(strip=True) if score_tag else ''
            
            # 類型（可能有多個）
            types_tag = item.select('.categories button')
            types = ', '.join([t.get_text(strip=True) for t in types_tag]) if types_tag else ''
            
            # 寫入 CSV
            writer.writerow([name, img_url, score, types])
        
        # 延遲避免被封
        time.sleep(1)

print("爬取完成，已存成 movie.csv")

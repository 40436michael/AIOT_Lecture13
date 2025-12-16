太好了，我幫你把 README 改成漂亮版，支援圖片插入、程式碼區塊高亮、表格清楚排版。下面你可以直接貼圖片路徑或 URL。

---

# Lecture 13 課堂練習 — 資料爬蟲 + SQLite + Streamlit

## 專案簡介

本作業分為兩個部分：

1. **中央氣象局資料 (CWA F-A0010-001)**

   * 下載 JSON 資料，解析各地區天氣資訊
   * 存入 SQLite 資料庫 `data.db`
   * 使用 Streamlit 顯示資料表格與資料分析
   https://aiotlecture13-es4px9tnrrqfte6xe2qeju.streamlit.app/
     

2. **電影網站爬蟲 (SSR1)**

   * 爬取 SSR1 前 10 頁電影資訊
   * 解析電影名稱、圖片 URL、評分、類型等欄位
   * 存成 CSV 檔 `movie.csv`

---

## Part 1：中央氣象局資料

### 1️⃣ 下載 JSON 資料

* API 下載 F-A0010-001 JSON：

```
https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?
```
<img width="657" height="1671" alt="image" src="https://github.com/user-attachments/assets/94044ede-c5f9-4a9d-9221-4b1d85237b50" />

* Python 範例程式碼：

```python
import requests
import json

API_KEY = "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F"
url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={API_KEY}&downloadType=WEB&format=JSON"
resp = requests.get(url)
data = resp.json()
with open("weather.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### 2️⃣ 解析資料並存入 SQLite

* SQLite DB：`data.db`
* 範例資料表設計：

```sql
CREATE TABLE weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    min_temp REAL,
    max_temp REAL,
    description TEXT
);
```

* Python 實作範例：

```python
import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    min_temp REAL,
    max_temp REAL,
    description TEXT
)
""")

# 假設已解析 JSON 得到 weather_list
cursor.executemany("""
INSERT INTO weather (location, min_temp, max_temp, description)
VALUES (?, ?, ?, ?)
""", weather_list)

conn.commit()
conn.close()
```

---

### 3️⃣ Streamlit 顯示資料

* 範例 `app.py`：

```python
import streamlit as st
import pandas as pd
import sqlite3

st.title("中央氣象局天氣資料")

conn = sqlite3.connect("data.db")
df = pd.read_sql("SELECT * FROM weather", conn)
conn.close()

st.dataframe(df)
```

* 範例截圖：

<img width="1763" height="588" alt="image" src="https://github.com/user-attachments/assets/8d6dd2a1-4c3a-4cb0-90bb-c55f22707ebb" />
<img width="1190" height="798" alt="image" src="https://github.com/user-attachments/assets/b9db98b8-313f-43e6-a143-4cd28077feca" />


---

## 📌 Part 2：電影網站爬蟲

### 1️⃣ 目標網站

* SSR1：[https://ssr1.scrape.center/](https://ssr1.scrape.center/)
* 10 頁：`page/1 ~ page/10`

---

### 2️⃣ 爬蟲程式

```python
import requests
from bs4 import BeautifulSoup
import csv
import time

output_file = 'movie.csv'
fields = ['電影名稱', '電影圖片 URL', '評分', '類型']

with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(fields)

    for page in range(1, 11):
        url = f"https://ssr1.scrape.center/page/{page}"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('.el-card')
        for item in items:
            name = item.select_one('.name').get_text(strip=True)
            img_url = item.select_one('img')['src']
            score_tag = item.select_one('.score')
            score = score_tag.get_text(strip=True) if score_tag else ''
            types = ', '.join([t.get_text(strip=True) for t in item.select('.categories button')])
            writer.writerow([name, img_url, score, types])
        time.sleep(1)
```

---

### 3️⃣ 輸出結果

* CSV：`movie.csv`
* 欄位：
電影名稱,電影圖片 URL,評分,類型

| 電影名稱   | 電影圖片 URL    | 評分  | 類型     |
| ------ | ----------- | --- | ------ |
| 霸王别姬   | https://... | 9.5 | 剧情, 爱情 |
| 肖申克的救赎 | https://... | 9.5 | 剧情, 犯罪 |

* 範例截圖：

<img width="800" height="676" alt="image" src="https://github.com/user-attachments/assets/a9d153f5-f14f-405c-a38b-a6e0999f40c4" />


---

## 交付內容清單

**Part 1**

* weather crawler Python 原始碼
* SQLite DB：`data.db`
* Streamlit App 原始碼
* Streamlit 顯示資料截圖

**Part 2**

* movie crawler Python 原始碼
* 產生的 `movie.csv`

---

## 使用方式

1. 先執行 `weather.py` 或 F-A0010-001 API 爬蟲，下載並存入 SQLite
2. 執行 `movie.py` 爬取電影資料
3. 執行 `app.py` 開啟 Streamlit，顯示資料表格與分析

---

## 📝 備註

* Streamlit 可自訂篩選條件、日期範圍、地點
* 爬蟲程式包含延遲，避免封鎖
* CSV 與 SQLite DB 結構簡單，方便後續分析


---




import requests
import urllib3
import json
import sqlite3
from config import API_KEY

# -------------------------
# 取消 SSL 驗證警告
# -------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------
# API URL
# -------------------------
URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-A0021-001?Authorization={API_KEY}&format=JSON"

# -------------------------
# 下載 JSON
# -------------------------
try:
    response = requests.get(URL, verify=False, timeout=15)
    response.raise_for_status()
    data = response.json()

    # 存成本地 JSON 檔
    with open("tide.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ JSON 已存成 tide.json")

except Exception as e:
    print("❌ API 下載錯誤:", e)
    exit()

# =========================
# 解析潮汐資料（全部日期）
# =========================
tide_list = []
locations = data["records"]["TideForecasts"]

for loc in locations:
    location_info = loc["Location"]
    location_name = location_info["LocationName"]
    location_id = location_info["LocationId"]
    latitude = location_info["Latitude"]
    longitude = location_info["Longitude"]
    daily_forecasts = location_info["TimePeriods"]["Daily"]
    
    for day in daily_forecasts:
        date = day["Date"]
        lunar_date = day.get("LunarDate", "")
        tide_range = day.get("TideRange", "")
        
        for time_entry in day["Time"]:
            datetime_str = time_entry["DateTime"]
            tide_type = time_entry.get("Tide", "")
            tide_heights = time_entry.get("TideHeights", {})

            # 安全轉 int
            def safe_int(val):
                try:
                    return int(val)
                except:
                    return None

            above_twvd = safe_int(tide_heights.get("AboveTWVD"))
            above_msl = safe_int(tide_heights.get("AboveLocalMSL"))
            above_cd = safe_int(tide_heights.get("AboveChartDatum"))

            tide_list.append((
                location_name, location_id, latitude, longitude,
                date, lunar_date, tide_range, datetime_str,
                tide_type,           # <-- TideType
                above_twvd, above_msl, above_cd
            ))

# =========================
# 存入 SQLite
# =========================
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# 建立資料表（如果不存在）
cursor.execute("""
CREATE TABLE IF NOT EXISTS tide (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    LocationName TEXT,
    LocationId TEXT,
    Latitude REAL,
    Longitude REAL,
    Date TEXT,
    LunarDate TEXT,
    TideRange TEXT,
    DateTime TEXT,
    TideType TEXT,
    AboveTWVD INTEGER,
    AboveLocalMSL INTEGER,
    AboveChartDatum INTEGER
)
""")

# 插入資料
cursor.executemany("""
INSERT INTO tide (
    LocationName, LocationId, Latitude, Longitude, Date, LunarDate,
    TideRange, DateTime, TideType, AboveTWVD, AboveLocalMSL, AboveChartDatum
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", tide_list)

conn.commit()
conn.close()
print(f"✅ 已將 {len(tide_list)} 筆潮汐資料存入 data.db")

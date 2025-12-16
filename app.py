# app.py
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# -------------------------
# 頁面設定
# -------------------------
st.set_page_config(page_title="台灣潮汐預報", layout="wide")
st.title("🌊 台灣潮汐預報（CWB F-A0021-001）")
st.markdown("透過 CWB F-A0021-001 API 資料提供未來潮汐預報")

# -------------------------
# 讀取資料
# -------------------------
conn = sqlite3.connect("data.db")
df = pd.read_sql("SELECT * FROM tide", conn, parse_dates=["Date", "DateTime"])
conn.close()

# -------------------------
# 左右欄佈局
# -------------------------
left_col, right_col = st.columns([1, 2])

# -------------------------
# 左欄: 篩選器
# -------------------------
with left_col:
    st.header("篩選條件")
    
    locations = df["LocationName"].unique()
    selected_location = st.selectbox("選擇地點", sorted(locations))
    
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    selected_dates = st.date_input("選擇日期範圍", [min_date, max_date])
    
    tide_type = st.selectbox("選擇潮位類型", ["滿潮", "乾潮"])

# -------------------------
# 篩選資料
# -------------------------
start_date, end_date = selected_dates

mask = (
    (df["LocationName"] == selected_location) &
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date)) &
    (df["TideType"] == tide_type)
)
df_filtered = df[mask].sort_values("DateTime")

# 使用 TideHeight 欄位
tide_height_column = "AboveTWVD"  # 可改成 AboveLocalMSL 或 AboveChartDatum
df_filtered = df_filtered[df_filtered[tide_height_column].notnull()]

if df_filtered.empty:
    st.warning("選擇的範圍沒有資料")
else:
    # -------------------------
    # 右欄: 資料表 & 圖表
    # -------------------------
    with right_col:
        st.subheader(f"{selected_location} {tide_type} 潮汐資料")
        st.dataframe(df_filtered.reset_index(drop=True), height=250)
        
        # -------------------------
        # 潮高摘要卡片
        # -------------------------
        st.subheader("📊 潮高摘要")
        max_tide = df_filtered[tide_height_column].max()
        min_tide = df_filtered[tide_height_column].min()
        mean_tide = df_filtered[tide_height_column].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("最高潮高", f"{max_tide:.1f} cm")
        col2.metric("最低潮高", f"{min_tide:.1f} cm")
        col3.metric("平均潮高", f"{mean_tide:.1f} cm")
        
        # -------------------------
        # 折線圖: Tide Height Curve
        # -------------------------
        st.subheader(f"📈 {tide_type} Tide Height Curve")
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10,4))

        # Plot tide height
        ax.plot(df_filtered["DateTime"], df_filtered[tide_height_column],
                marker="o", color="#1f77b4", linestyle='-', linewidth=2, label=tide_type)

        # Highlight max and min
        max_idx = df_filtered[tide_height_column].idxmax()
        min_idx = df_filtered[tide_height_column].idxmin()
        ax.scatter(df_filtered.loc[max_idx, "DateTime"], df_filtered.loc[max_idx, tide_height_column],
                color="red", s=100, label="Max Tide")
        ax.scatter(df_filtered.loc[min_idx, "DateTime"], df_filtered.loc[min_idx, tide_height_column],
                color="green", s=100, label="Min Tide")

        # Legend in lower left
        ax.legend(loc="lower left")

        ax.set_xlabel("DateTime")
        ax.set_ylabel("Tide Height (cm)")
        ax.set_title(f"{selected_location} {tide_type} Tide Height Trend")
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        st.pyplot(fig)
        
        # -------------------------
        # 滾動區塊: 詳細資料
        # -------------------------
        with st.expander("📋 查看完整潮汐資料表"):
            st.dataframe(df_filtered.reset_index(drop=True))

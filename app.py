import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import json
import os

DATA_FILE = "records.json"

# 初始化
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_records = json.load(f)
    st.session_state.records = [
        {
            "日期": datetime.strptime(r["日期"], "%Y-%m-%d").date(),
            "分類": r["分類"],
            "金額": r["金額"],
            "備註": r["備註"]
        }
        for r in raw_records
    ]
else:
    st.session_state.records = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.set_page_config(page_title="簡單記帳", page_icon="📒")
st.title("📒 簡單記帳 App")

def save_records():
    to_save = [
        {
            "日期": r["日期"].strftime("%Y-%m-%d"),
            "分類": r["分類"],
            "金額": r["金額"],
            "備註": r["備註"]
        }
        for r in st.session_state.records
    ]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)

# 輸入表單區塊
st.header("✏️ 新增 / 修改支出")
col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("📅 日期", value=date.today())
    input_category = st.selectbox("📂 分類", ["🍔 餐飲", "🚇 交通", "🍿 娛樂", "🛒 生活用品", "📦 其他"])
with col2:
    input_amount = st.number_input("💵 金額", min_value=0.0, format="%.2f")
    input_note = st.text_input("📝 備註", "")

if st.session_state.edit_index is None:
    if st.button("➕ 新增"):
        if input_amount > 0:
            st.session_state.records.append({
                "日期": input_date,
                "分類": input_category,
                "金額": input_amount,
                "備註": input_note
            })
            save_records()
            st.success("✅ 新增成功！")
        else:
            st.error("⚠️ 金額需大於 0")
else:
    if st.button("✅ 確認修改"):
        st.session_state.records[st.session_state.edit_index] = {
            "日期": input_date,
            "分類": input_category,
            "金額": input_amount,
            "備註": input_note
        }
        save_records()
        st.session_state.edit_index = None
        st.success("✏️ 修改完成")
        st.experimental_rerun()

# 顯示帳目清單
st.header("📋 帳目清單")

if not st.session_state.records:
    st.info("目前沒有資料喔！")
else:
    df = pd.DataFrame(st.session_state.records)
    df = df.sort_values(by="日期").reset_index(drop=True)

    df['日期顯示'] = df['日期'].astype(str)
    prev_date = ""
    for i in range(len(df)):
        if df.at[i, '日期顯示'] == prev_date:
            df.at[i, '日期顯示'] = ""
        else:
            prev_date = df.at[i, '日期顯示']

    for idx, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.5, 1.5, 2, 1, 1])
        with col1:
            st.markdown(row['日期顯示'])
        with col2:
            st.markdown(row['分類'])
        with col3:
            st.markdown(f"NT${row['金額']:.2f}")
        with col4:
            st.markdown(row['備註'] or "—")
        with col5:
            if st.button("✏️", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
                selected = st.session_state.records[idx]
                st.experimental_rerun()
        with col6:
            if st.button("🗑️", key=f"delete_{idx}"):
                st.session_state.records.pop(idx)
                save_records()
                st.success("✅ 已刪除")
                st.experimental_rerun()

# 統計圖表
if st.session_state.records:
    st.subheader("📊 各分類支出圖")
    chart_data = pd.DataFrame(st.session_state.records).groupby("分類")["金額"].sum().reset_index()
    fig = px.pie(chart_data, names="分類", values="金額", title="分類支出比例", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    # 匯出 CSV
    csv_data = pd.DataFrame(st.session_state.records).to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 匯出目前資料為 CSV", data=csv_data, file_name="記帳資料.csv", mime="text/csv")

import streamlit as st
import pandas as pd
from datetime import date

# 初始化 session_state 裡的資料
if "records" not in st.session_state:
    st.session_state.records = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.set_page_config(page_title="記帳 App", page_icon="💰")
st.title("💰 我的記帳小幫手")

st.markdown("快速記錄每筆支出，並自動統計分類支出。")

# 📌 新增或編輯區塊
st.header("✏️ 輸入或修改資料")

col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("📅 日期", value=date.today())
    input_category = st.selectbox("📂 分類", ["餐飲", "交通", "娛樂", "生活用品", "其他"])
with col2:
    input_amount = st.number_input("💵 金額", min_value=0.0, format="%.2f")
    input_note = st.text_input("📝 備註", "")

# 按鈕功能（新增或更新）
if st.session_state.edit_index is None:
    if st.button("➕ 新增帳目"):
        if input_amount > 0:
            new_record = {
                "日期": input_date,
                "分類": input_category,
                "金額": input_amount,
                "備註": input_note
            }
            st.session_state.records.append(new_record)
            st.success("✅ 新增成功！")
        else:
            st.error("⚠️ 金額必須大於 0")
else:
    if st.button("✅ 確認修改"):
        index = st.session_state.edit_index
        st.session_state.records[index] = {
            "日期": input_date,
            "分類": input_category,
            "金額": input_amount,
            "備註": input_note
        }
        st.session_state.edit_index = None
        st.success("✏️ 修改成功！")

# 顯示目前紀錄
st.header("📊 帳目清單")

if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)

    # 顯示可編輯紀錄表格
    for i, row in df.iterrows():
        st.markdown(f"**{row['日期']} | {row['分類']} | NT${row['金額']:.2f}**")
        st.caption(f"備註：{row['備註']}")
        cols = st.columns([1, 1])
        if cols[0].button("✏️ 修改", key=f"edit{i}"):
            st.session_state.edit_index = i
            # 把資料填回輸入欄
            input_date = row["日期"]
            input_category = row["分類"]
            input_amount = row["金額"]
            input_note = row["備註"]
        if cols[1].button("🗑️ 刪除", key=f"delete{i}"):
            st.session_state.records.pop(i)
            st.experimental_rerun()
        st.divider()
else:
    st.info("目前尚無紀錄，請新增帳目。")

# 分類統計圖表
if st.session_state.records:
    st.subheader("📈 各分類支出圖表")
    chart_data = df.groupby("分類")["金額"].sum()
    st.bar_chart(chart_data)

import streamlit as st
import pandas as pd

# 初始化 session_state 裡的資料
if "records" not in st.session_state:
    st.session_state.records = []

st.title("簡易記帳 App")

# 輸入區
st.header("新增帳目")
date = st.date_input("日期")
category = st.selectbox("分類", ["餐飲", "交通", "娛樂", "生活用品", "其他"])
amount = st.number_input("金額", min_value=0)
note = st.text_input("備註")

if st.button("新增"):
    new_record = {"日期": date, "分類": category, "金額": amount, "備註": note}
    st.session_state.records.append(new_record)
    st.success("已新增一筆帳目 ✅")

# 顯示目前紀錄
st.header("帳目紀錄")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df)

    # 圖表統計
    st.subheader("各分類支出圖表")
    chart_data = df.groupby("分類")["金額"].sum()
    st.bar_chart(chart_data)
else:
    st.info("目前尚無紀錄")

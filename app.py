import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# 初始化 session_state
if "records" not in st.session_state:
    st.session_state.records = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.set_page_config(page_title="每日花費記帳&消費分析", page_icon="📒")
st.title("📒  我的記帳小幫手")
st.markdown("記錄你的每日支出，簡單好用、圖表清晰！")

# ➤ 篩選月份
all_dates = [r["日期"] for r in st.session_state.records]
all_months = sorted(list(set([d.strftime("%Y-%m") for d in all_dates])))

selected_month = st.selectbox("📅 選擇月份（空白代表全部）", [""] + all_months)

def filter_by_month(records, month):
    if not month:
        return records
    return [r for r in records if r["日期"].strftime("%Y-%m") == month]

filtered_records = filter_by_month(st.session_state.records, selected_month)

# ➤ 輸入區塊
st.header("✏️ 新增或修改支出")
col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("📅  日期", value=date.today())
    input_category = st.selectbox("📂 分類", ["🍔  餐飲", "🚇  交通", "🍿  娛樂", "🛒  生活用品", "📦  其他"])
with col2:
    input_amount = st.number_input("💵  金額", min_value=0.0, format="%.2f")
    input_note = st.text_input("📝  備註", "")

if st.session_state.edit_index is None:
    if st.button("➕ 新增"):
        if input_amount > 0:
            st.session_state.records.append({
                "日期": input_date,
                "分類": input_category,
                "金額": input_amount,
                "備註": input_note
            })
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
        st.session_state.edit_index = None
        st.success("✏️ 修改完成")

# ➤ 表格顯示函式：同一天只顯示一次日期，日期由早到晚排序
def show_accounting_table(records):
    if not records:
        st.info("目前沒有資料喔！")
        return

    df = pd.DataFrame(records)
    # 日期由早到晚排序（升冪）
    df = df.sort_values(by="日期", ascending=True).reset_index(drop=True)

    # 日期欄位做群組：同一天只顯示一次日期
    df['日期顯示'] = df['日期'].astype(str)
    prev_date = ""
    for i in range(len(df)):
        if df.at[i, '日期顯示'] == prev_date:
            df.at[i, '日期顯示'] = ""
        else:
            prev_date = df.at[i, '日期顯示']

    df_display = df[['日期顯示', '分類', '金額', '備註']].copy()
    df_display.columns = ['日期', '分類', '金額', '備註']

    # 格式化金額顯示
    df_display['金額'] = df_display['金額'].apply(lambda x: f"NT${x:.2f}")

    # 重新設定 index 從 1 開始
    df_display.index = range(1, len(df_display) + 1)

    st.table(df_display)

# ➤ 顯示帳目清單
st.header("📋 帳目清單")
show_accounting_table(filtered_records)

# ➤ 修改與刪除功能
if filtered_records:
    df = pd.DataFrame(filtered_records)
    df = df.sort_values(by="日期", ascending=True).reset_index(drop=True)
    st.markdown("---")
    st.header("🔧  修改或刪除")

    selected_row = st.number_input("請輸入要修改或刪除的編號", min_value=1, max_value=len(df), step=1)
    selected_index = df.index[selected_row - 1]

    col3, col4 = st.columns(2)
    if col3.button("✏️  修改這筆"):
        selected_record = df.iloc[selected_index].to_dict()
        for i, rec in enumerate(st.session_state.records):
            if rec == selected_record:
                st.session_state.edit_index = i
                break
        st.experimental_rerun()

    if col4.button("🗑️  刪除這筆"):
        selected_record = df.iloc[selected_index].to_dict()
        for i, rec in enumerate(st.session_state.records):
            if rec == selected_record:
                st.session_state.records.pop(i)
                break
        st.success("✅  已刪除")
        st.experimental_rerun()

# ➤ 匯出 CSV
if filtered_records:
    csv_data = pd.DataFrame(filtered_records).to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥  匯出目前資料為 CSV", data=csv_data, file_name="記帳資料.csv", mime="text/csv")

# ➤ 圖表區
if filtered_records:
    st.subheader("📊  各分類支出圖")
    chart_data = pd.DataFrame(filtered_records).groupby("分類")["金額"].sum().reset_index()
    fig = px.pie(chart_data, names="分類", values="金額", title="分類支出比例", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

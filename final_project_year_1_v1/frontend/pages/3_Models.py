import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from utils.http_client import api_get, parse_response

st.title("История моделей")

col1, col2 = st.columns(2)
with col1:
    if st.button("Обновить", type="primary"):
        st.rerun()
with col2:
    status_filter = st.selectbox(
        "Фильтр по статусу",
        ["Все", "done", "pending", "failed"],
    )

params = {}
if status_filter != "Все":
    params["status"] = status_filter

resp = api_get("/results", params=params)
data, err = parse_response(resp)
if err:
    st.error(f"Не удалось загрузить результаты: {err}")
    st.stop()

results = data.get("results", [])
if not results:
    st.info("Пока нет записей. Обучите модель на странице Train.")
    st.stop()

df = pd.DataFrame(results)
display_cols = [
    "id", "model_name", "dataset", "algorithm", "train_size",
    "status", "mae", "rmse", "r2", "created_at", "finished_at",
]
existing = [c for c in display_cols if c in df.columns]
st.dataframe(df[existing], use_container_width=True)

done = df[df["status"] == "done"].copy() if "status" in df.columns else pd.DataFrame()
if not done.empty and "r2" in done.columns:
    st.subheader("Сравнение метрик (успешные запуски)")
    chart_df = done.set_index("model_name")[["mae", "rmse", "r2"]]
    st.bar_chart(chart_df[["mae", "rmse"]])
    st.line_chart(chart_df[["r2"]])

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from utils.http_client import api_get, api_post, parse_response

st.title("Обучение модели")

ALGO_LABELS = {
    "linear_regression": "Linear Regression",
    "random_forest": "Random Forest",
    "ridge": "Ridge",
}

files_resp = api_get("/files")
files_data, files_err = parse_response(files_resp)
if files_err:
    st.error(f"API недоступен: {files_err}")
    st.stop()

files = files_data.get("files", [])
default_file = "boston_housing.csv" if "boston_housing.csv" in files else (files[0] if files else "")

algo_resp = api_get("/algorithms")
algo_data, _ = parse_response(algo_resp)
algorithms = algo_data.get("algorithms", list(ALGO_LABELS)) if algo_data else list(ALGO_LABELS)

with st.form("train_form"):
    filename = st.selectbox("Файл данных", files, index=files.index(default_file) if default_file in files else 0) if files else st.text_input("Файл данных (нет CSV в data/)")
    model_name = st.text_input("Название модели", value="boston_lr_v1")
    algorithm = st.selectbox(
        "Алгоритм",
        algorithms,
        format_func=lambda k: ALGO_LABELS.get(k, k),
    )
    train_size = st.slider("Доля обучающей выборки", 0.1, 0.9, 0.8, 0.05)
    target_column = st.text_input("Целевой столбец (пусто = MEDV или последний)", value="")
    submit = st.form_submit_button("Обучить модель")

if submit:
    if not filename or not model_name:
        st.warning("Укажите файл и имя модели")
    else:
        payload = {
            "filename": filename,
            "model_name": model_name,
            "algorithm": algorithm,
            "train_size": train_size,
        }
        if target_column.strip():
            payload["target_column"] = target_column.strip()

        resp = api_post("/train", json=payload)
        data, err = parse_response(resp)
        if err:
            st.error(err)
        else:
            st.session_state["last_result_id"] = data["result_id"]
            st.success(data["message"])
            st.json(data)

result_id = st.session_state.get("last_result_id")
if result_id:
    st.subheader("Статус обучения")
    status_box = st.empty()
    if st.button("Проверить статус"):
        for _ in range(30):
            r = api_get(f"/results/{result_id}")
            row, err = parse_response(r)
            if err:
                status_box.error(err)
                break
            status = row.get("status")
            status_box.info(f"Статус: **{status}**")
            if status == "done":
                st.metric("MAE", f"{row['mae']:.4f}")
                st.metric("RMSE", f"{row['rmse']:.4f}")
                st.metric("R²", f"{row['r2']:.4f}")
                break
            if status == "failed":
                st.error(row.get("error_message", "Ошибка обучения"))
                break
            time.sleep(1)
        else:
            status_box.warning("Обучение ещё выполняется. Нажмите «Проверить статус» снова.")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from utils.http_client import api_get, api_post, parse_response
from utils.paths import BOSTON_FEATURES

st.title("Прогноз цены")

DEFAULTS = {
    "crim": 0.00632,
    "zn": 18.0,
    "indus": 2.31,
    "chas": 0,
    "nox": 0.538,
    "rm": 6.575,
    "age": 65.2,
    "dis": 4.09,
    "rad": 1,
    "tax": 296,
    "ptratio": 15.3,
    "b": 396.9,
    "lstat": 4.98,
}

resp = api_get("/results", params={"status": "done"})
data, err = parse_response(resp)
if err:
    st.error(f"API недоступен: {err}")
    st.stop()

results = data.get("results", [])
model_names = [r["model_name"] for r in results]
if not model_names:
    st.warning("Нет обученных моделей. Сначала обучите модель на странице Train.")
    st.stop()

model_name = st.selectbox("Модель", model_names)

st.caption("MEDV — медианная стоимость домов в $1000 (типичный диапазон 5–50).")

with st.form("predict_form"):
    features = {}
    cols = st.columns(3)
    for i, name in enumerate(BOSTON_FEATURES):
        with cols[i % 3]:
            features[name] = st.number_input(
                name,
                value=float(DEFAULTS[name]),
                format="%.5f" if name in ("crim", "nox") else "%.2f",
            )
    submit = st.form_submit_button("Предсказать MEDV")

if submit:
    r = api_post("/predict", json={"model_name": model_name, "features": features})
    out, err = parse_response(r)
    if err:
        st.error(err)
    else:
        price = out["predicted_medv"]
        st.success(f"Прогноз MEDV: **{price:.2f}** (≈ ${price * 1000:,.0f} в ценах датасета)")
        st.json(out)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from utils.paths import DATA_DIR

DATA_DIR.mkdir(exist_ok=True)

st.title("Данные")

st.markdown(
    "Демо-файл: `data/boston_housing.csv` (506 объектов, целевая колонка **MEDV**)."
)

f = st.file_uploader("Загрузить CSV", type=["csv"])
if f:
    dest = DATA_DIR / f.name
    dest.write_bytes(f.getvalue())
    st.success(f"Файл сохранён: {f.name}")

files = sorted(p.name for p in DATA_DIR.glob("*.csv"))
name = st.selectbox("Файлы в data/", files) if files else None

if name:
    df = pd.read_csv(DATA_DIR / name)
    st.subheader(name)
    st.write(f"Строк: {len(df)}, столбцов: {len(df.columns)}")
    target = "MEDV" if "MEDV" in df.columns else ("medv" if "medv" in df.columns else df.columns[-1])
    st.caption(f"Целевая переменная (по умолчанию): **{target}**")
    st.dataframe(df.head(20), use_container_width=True)
    if target in df.columns:
        st.line_chart(df[target].reset_index(drop=True))

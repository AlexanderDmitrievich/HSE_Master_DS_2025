import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

st.set_page_config(
    page_title="Цены на жильё — Boston Housing",
    layout="wide",
)

st.title("Прогноз цен на жильё (Boston Housing)")
st.markdown(
    """
Сервис для работы с датасетом **Boston Housing**: загрузка данных, обучение моделей
регрессии через **FastAPI**, просмотр экспериментов и предсказание целевой переменной **MEDV**
(медианная стоимость домов, $1000).

**Страницы:**
1. **Data** — загрузка и просмотр CSV
2. **Train** — запуск обучения (Linear Regression, Random Forest, Ridge)
3. **Models** — история экспериментов и метрики MAE / RMSE / R²
4. **Predict** — прогноз цены по признакам

Перед работой запустите API: `uvicorn backend.api:app --reload`
"""
)

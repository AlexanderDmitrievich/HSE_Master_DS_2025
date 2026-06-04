# Цены на жильё — Boston Housing

Учебный ML-сервис: **Streamlit** (UI) + **FastAPI** (обучение и инференс) + **SQLite** (история экспериментов).

Целевая переменная: **MEDV** — медианная стоимость домов (в $1000).  
Датасет: [Boston Housing](https://www.kaggle.com/datasets/altavish/boston-housing-dataset) (`data/boston_housing.csv`, 506 строк).

## Архитектура

```
  UI[Streamlit] -->|HTTP| API[FastAPI]
  API -->|background| Train[sklearn train]
  Train --> DB[(SQLite)]
  Train --> PKL[models/*.pkl]
  UI -->|GET /results, POST /predict| API
  API --> PKL
```

## Запуск

```bash
conda deactivate   # при необходимости, пока (base) не исчезнет
deactivate 2>/dev/null || true   # выйти из старого venv, если был активен

# если myvenv копировали с другого проекта или pip/python «не найдены» — пересоздайте:
rm -rf myvenv
python3 -m venv myvenv
source myvenv/bin/activate

python -m pip install -r requirements.txt
python utils/init_db.py
```

> После `conda deactivate` снова выполните `source myvenv/bin/activate`.  
> Если `pip` не находится, всегда можно: `python -m pip install -r requirements.txt`

Терминал 1 — API:

```bash
python -m uvicorn backend.api:app --reload
```

Терминал 2 — UI:

```bash
streamlit run frontend/Main.py
```

Или один скрипт (API + Streamlit):

```bash
chmod +x run.sh
./run.sh
```

- UI: http://localhost:8501/
- API docs: http://localhost:8000/docs

Переменная окружения для фронта: `API_URL=http://localhost:8000` (по умолчанию).

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка сервиса |
| GET | `/files` | Список CSV в `data/` |
| GET | `/algorithms` | Доступные алгоритмы |
| POST | `/train` | Запуск обучения (фон) |
| GET | `/results` | История (`?status=done`) |
| GET | `/results/{id}` | Одна запись |
| POST | `/predict` | Прогноз MEDV |

Пример обучения:

```json
{
  "filename": "boston_housing.csv",
  "model_name": "boston_rf_v1",
  "algorithm": "random_forest",
  "train_size": 0.8
}
```

Пример предсказания:

```json
{
  "model_name": "boston_rf_v1",
  "features": {
    "crim": 0.01, "zn": 18, "indus": 2.3, "chas": 0, "nox": 0.53,
    "rm": 6.5, "age": 65, "dis": 4.0, "rad": 1, "tax": 296,
    "ptratio": 15.3, "b": 396.9, "lstat": 5.0
  }
}
```

## Алгоритмы

- `linear_regression` — Linear Regression
- `random_forest` — Random Forest Regressor
- `ridge` — Ridge

Метрики на тесте: **MAE**, **RMSE**, **R²**.

## Структура проекта

```
backend/
  api.py
  ml/
    train.py
    predict.py
frontend/
  Main.py
  pages/
    1_Data.py
    2_Train.py
    3_Models.py
    4_Predict.py
utils/
  paths.py
  db.py
  init_db.py
  http_client.py
data/
  boston_housing.csv
models/          # артефакты .pkl (в .gitignore)
models.db        # SQLite (в .gitignore)
```

## Типичные ошибки

- **`command not found: pip` / `python`** — пересоздайте `myvenv` (см. выше) или заново `source myvenv/bin/activate` после `conda deactivate`.
- **Address already in use (порт 8000)** — остановите старый процесс: `lsof -i :8000` и `kill <PID>`, либо запустите на другом порту: `python -m uvicorn backend.api:app --reload --port 8001`.
- **API недоступен** — запустите `uvicorn` до Streamlit.
- **Модель с таким именем уже существует** — выберите новое `model_name`.
- **Файл не найден** — загрузите CSV на странице Data или используйте `boston_housing.csv`.

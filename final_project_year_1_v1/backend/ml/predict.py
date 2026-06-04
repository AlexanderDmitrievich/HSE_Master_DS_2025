import json
import pickle
from pathlib import Path

import pandas as pd

from utils.paths import MODELS_DIR


def predict_price(model_name: str, features: dict[str, float]) -> dict:
    model_path = MODELS_DIR / f"{model_name}.pkl"
    if not model_path.is_file():
        raise FileNotFoundError(f"Модель '{model_name}' не найдена")

    with open(model_path, "rb") as f:
        artifact = pickle.load(f)

    model = artifact["model"]
    feature_columns = artifact["feature_columns"]
    target_column = artifact["target_column"]

    normalized = {_normalize_key(k): v for k, v in features.items()}
    row = {}
    for col in feature_columns:
        key = _normalize_key(col)
        if key not in normalized:
            raise ValueError(f"Не передан признак '{col}'")
        row[col] = normalized[key]

    X = pd.DataFrame([row], columns=feature_columns)
    prediction = float(model.predict(X)[0])

    return {
        "model_name": model_name,
        "predicted_medv": prediction,
        "target_column": target_column,
        "features_used": row,
    }


def _normalize_key(name: str) -> str:
    return name.strip().lower()

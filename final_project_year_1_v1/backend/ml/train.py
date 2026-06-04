import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from utils.db import mark_done, mark_failed
from utils.paths import DATA_DIR, DEFAULT_TARGET, MODELS_DIR

ALGORITHMS = {
    "linear_regression": LinearRegression,
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=100, random_state=42
    ),
    "ridge": lambda: Ridge(alpha=1.0),
}


def validate_dataset(df: pd.DataFrame, target_column: str) -> None:
    if len(df) < 10:
        raise ValueError("В датасете должно быть не менее 10 строк")

    if target_column not in df.columns:
        raise ValueError(f"Целевой столбец '{target_column}' не найден")

    if df[target_column].isna().any():
        raise ValueError("В целевом столбце есть пропуски")

    feature_cols = [c for c in df.columns if c != target_column]
    if not feature_cols:
        raise ValueError("Нет признаков для обучения")

    features = df[feature_cols]
    if features.isna().any().any():
        raise ValueError("В признаках есть пропуски")

    if not np.issubdtype(df[target_column].dtype, np.number):
        raise ValueError("Целевой столбец должен быть числовым")

    for col in feature_cols:
        if not np.issubdtype(df[col].dtype, np.number):
            raise ValueError(f"Признак '{col}' должен быть числовым")


def resolve_target_column(df: pd.DataFrame, target_column: str | None) -> str:
    if target_column:
        return target_column
    for candidate in (DEFAULT_TARGET, "medv", "MEDV"):
        if candidate in df.columns:
            return candidate
    return df.columns[-1]


def build_model(algorithm: str):
    if algorithm not in ALGORITHMS:
        raise ValueError(
            f"Неизвестный алгоритм: {algorithm}. Доступны: {list(ALGORITHMS)}"
        )
    factory = ALGORITHMS[algorithm]
    if isinstance(factory, type):
        return factory()
    return factory()


def train_model(
    result_id: int,
    filename: str,
    model_name: str,
    algorithm: str,
    train_size: float,
    target_column: str | None = None,
) -> None:
    try:
        path = DATA_DIR / filename
        df = pd.read_csv(path)
        target = resolve_target_column(df, target_column)
        validate_dataset(df, target)

        X = df.drop(columns=[target])
        y = df[target]
        feature_columns = list(X.columns)

        if not 0.1 <= train_size <= 0.9:
            raise ValueError("train_size должен быть в диапазоне от 0.1 до 0.9")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=train_size, random_state=42
        )

        model = build_model(algorithm)
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        mae = float(mean_absolute_error(y_test, pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        r2 = float(r2_score(y_test, pred))
        metrics = {"mae": mae, "rmse": rmse, "r2": r2}

        MODELS_DIR.mkdir(exist_ok=True)
        model_path = MODELS_DIR / f"{model_name}.pkl"
        artifact = {
            "model": model,
            "feature_columns": feature_columns,
            "target_column": target,
            "algorithm": algorithm,
        }
        with open(model_path, "wb") as f:
            pickle.dump(artifact, f)

        mark_done(
            result_id=result_id,
            mae=mae,
            rmse=rmse,
            r2=r2,
            metrics=metrics,
            model_path=str(model_path),
            feature_columns=feature_columns,
        )
    except Exception as exc:
        mark_failed(result_id, str(exc))

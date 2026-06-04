from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.ml.predict import predict_price
from backend.ml.train import ALGORITHMS, train_model
from utils.db import fetch_result, fetch_results, insert_pending, model_name_exists
from utils.paths import DATA_DIR

app = FastAPI(
    title="Boston Housing ML API",
    description="Обучение и предсказание цен на жильё (Boston Housing)",
)

AlgorithmName = Literal["linear_regression", "random_forest", "ridge"]


class TrainRequest(BaseModel):
    filename: str
    model_name: str
    algorithm: AlgorithmName = "linear_regression"
    train_size: float = Field(0.8, ge=0.1, le=0.9)
    target_column: str | None = None


class PredictRequest(BaseModel):
    model_name: str
    features: dict[str, float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/files")
def list_data_files():
    DATA_DIR.mkdir(exist_ok=True)
    files = sorted(
        f.name for f in DATA_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".csv"
    )
    return {"files": files}


@app.get("/algorithms")
def list_algorithms():
    return {"algorithms": list(ALGORITHMS.keys())}


@app.get("/results")
def get_results(status: str | None = None):
    if status and status not in {"pending", "done", "failed"}:
        raise HTTPException(status_code=400, detail="Недопустимый status")
    return {"results": fetch_results(status)}


@app.get("/results/{result_id}")
def get_result(result_id: int):
    row = fetch_result(result_id)
    if not row:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return row


@app.post("/train")
def train(req: TrainRequest, background_tasks: BackgroundTasks):
    path = DATA_DIR / req.filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Файл данных не найден")

    if model_name_exists(req.model_name):
        raise HTTPException(
            status_code=400,
            detail=f"Модель с именем '{req.model_name}' уже существует",
        )

    target_column = req.target_column or "MEDV"
    result_id = insert_pending(
        model_name=req.model_name,
        dataset=req.filename,
        algorithm=req.algorithm,
        train_size=req.train_size,
        target_column=target_column,
    )

    background_tasks.add_task(
        train_model,
        result_id,
        req.filename,
        req.model_name,
        req.algorithm,
        req.train_size,
        req.target_column,
    )
    return {
        "message": "Модель отправлена на обучение",
        "result_id": result_id,
        "status": "pending",
    }


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        return predict_price(req.model_name, req.features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

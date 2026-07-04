from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "modelo.pkl"
STATIC_DIR = BASE_DIR / "static"

FEATURE_COLUMNS = [
    "grupo_sanguineo",
    "fumante",
    "nivel_atividade_fisica",
    "idade",
    "peso",
    "altura",
]


class PredictionInput(BaseModel):
    grupo_sanguineo: str = Field(..., description="A, B, AB ou O")
    fumante: str = Field(..., description="Sim ou Nao")
    nivel_atividade_fisica: str = Field(..., description="Baixo, Moderado ou Alto")
    idade: int = Field(..., ge=0, le=120)
    peso: float = Field(..., gt=0, le=350)
    altura: int = Field(..., ge=50, le=250)

    @field_validator("grupo_sanguineo")
    @classmethod
    def validate_blood_type(cls, value: str) -> str:
        normalized = value.strip().upper()
        allowed = {"A", "B", "AB", "O"}
        if normalized not in allowed:
            raise ValueError("grupo_sanguineo deve ser A, B, AB ou O")
        return normalized

    @field_validator("fumante")
    @classmethod
    def validate_smoker(cls, value: str) -> str:
        normalized = value.strip().lower()
        mapping = {
            "sim": "Sim",
            "s": "Sim",
            "nao": "Não",
            "não": "Não",
            "n": "Não",
        }
        if normalized not in mapping:
            raise ValueError("fumante deve ser Sim ou Nao")
        return mapping[normalized]

    @field_validator("nivel_atividade_fisica")
    @classmethod
    def validate_activity_level(cls, value: str) -> str:
        normalized = value.strip().lower()
        mapping = {
            "baixo": "Baixo",
            "moderado": "Moderado",
            "alto": "Alto",
        }
        if normalized not in mapping:
            raise ValueError("nivel_atividade_fisica deve ser Baixo, Moderado ou Alto")
        return mapping[normalized]


class PredictionOutput(BaseModel):
    colesterol: float
    unidade: str = "mg/dL"
    entrada: PredictionInput


@lru_cache(maxsize=1)
def load_model() -> Any:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo nao encontrado em {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


app = FastAPI(
    title="Preditor de Colesterol",
    description="API para prever colesterol com base em caracteristicas pessoais.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    try:
        load_model()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput) -> PredictionOutput:
    try:
        model = load_model()
        data = pd.DataFrame([payload.model_dump()])[FEATURE_COLUMNS]
        prediction = float(model.predict(data)[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar predicao: {exc}") from exc

    return PredictionOutput(
        colesterol=round(prediction, 2),
        entrada=payload,
    )

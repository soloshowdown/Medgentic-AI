"""FastAPI server exposing the hospital prediction endpoint."""
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from agents.coordinator_agent import run_prediction_pipeline


class PredictionRequest(BaseModel):
    city: str = Field(..., description="City name (e.g., Mumbai)")
    date: str = Field(..., description="Target date in YYYY-MM-DD")

    @validator("date")
    def validate_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("date must be in YYYY-MM-DD format") from exc
        return value


app = FastAPI(
    title="Predictive Hospital Management API",
    version="1.0.0",
    description="Agentic AI system to predict hospital surges in Indian cities.",
)

# Allow local dev origins (Next.js frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/predict")
async def predict(req: PredictionRequest):
    """Run the full coordinator pipeline."""
    try:
        result = run_prediction_pipeline(city=req.city, date=req.date)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


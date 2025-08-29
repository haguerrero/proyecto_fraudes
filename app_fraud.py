from fastapi import FastAPI
from pydantic import BaseModel
import joblib, json
import pandas as pd
import os
from typing import Optional

# Initialize FastAPI app
BASE_DIR = os.path.join(os.path.dirname(__file__), 'modelo')

# Load the pre-trained model
model = joblib.load(os.path.join(BASE_DIR, 'fraud_model_v3.joblib'))

with open(os.path.join(BASE_DIR, "metadata.json")) as f:
    metadata = json.load(f)

with open(os.path.join(BASE_DIR, "feature_spec.json")) as f:
    feature_spec = json.load(f)

THRESHOLD = metadata["best_threshold"]
FEATURES = feature_spec["columns"]

app = FastAPI(
    title="Fraud Detection API",
    description="API para predecir transacciones de fraudes usando XGBClassifier.",
    version="1.0.0",
)


class Transaction(BaseModel):
    TransactionID: Optional[int] = None
    step: int
    amount: float
    type_CASH_OUT: bool
    type_DEBIT: bool
    type_PAYMENT: bool
    type_TRANSFER: bool

class TransactioninBatch(BaseModel):
    transactions: list[Transaction]

@app.post("/predict")
def predict(transaction: Transaction):
    data = pd.DataFrame([transaction.model_dump()])[FEATURES]

    y_proba = model.predict_proba(data)[:, 1][0]
    y_pred = int(y_proba >= THRESHOLD)

    return {
        "trasaction_id": transaction.model_dump(),
        "probability": float(y_proba),
        "prediction": y_pred,
        "threshold": THRESHOLD,
        "metadata": {
            "model_version": metadata["model_version"],
            "model_type": metadata["model_type"],
            "model_name": metadata["model_name"],
        }
    }

@app.post("/predict_batch")
def predict_batch(transactions: TransactioninBatch):

    tx_list = transactions.model_dump()["transactions"]

    data = pd.DataFrame(tx_list)[FEATURES]

    y_proba = model.predict_proba(data)[:, 1]
    y_pred = (y_proba >= THRESHOLD).astype(int)

    results = []

    for tx, proba, pred in zip(tx_list, y_proba, y_pred):
        results.append({
            "transaction": tx,
            "probability": float(proba),
            "prediction": int(pred),
            "threshold": THRESHOLD
        })

    return {
        "results": results,
        "metadata": {
            "model_version": metadata["model_version"],
            "model_type": metadata["model_type"],
            "model_name": metadata["model_name"],
        }
    }

@app.get("/")
def read_root():
    return {
        "message": "🚀 Fraud Detection API is running!",
        "model_name": metadata["model_name"],
        "model_version": metadata["model_version"],
        "threshold": THRESHOLD
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
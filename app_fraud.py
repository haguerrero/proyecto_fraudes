from fastapi import FastAPI, Query
from pydantic import BaseModel
import joblib, json
import pandas as pd
import numpy as np
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
    TransactionID: Optional[str] = None
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
    frauds = []

    for tx, proba, pred in zip(tx_list, y_proba, y_pred):
        result = {
            "transaction": tx,
            "probability": float(proba),
            "prediction": int(pred),
            
        }

        results.append(result)
        if pred == 1:
            frauds.append(result)

    summary = {
        "total_transactions": len(results),
        "frauds_detected": len(frauds),
        "fraud_transactions": frauds
    }

    return {
        "results": results,
        "summary": summary,
        "metadata": {
            "model_version": metadata["model_version"],
            "model_type": metadata["model_type"],
            "model_name": metadata["model_name"],
            "threshold": THRESHOLD
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

@app.get("/generate_transactions")
def generate_transactions(number: int = Query(10, description="Número de transacciones a generar")):
    steps = np.random.randint(1, 744, size=number)
    amounts = np.round(np.random.uniform(0.0, 100000.0, size=number), 2)
    types = np.random.choice(["CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"], size=number)
    transactions = [
        {
            "TransactionID": f"SIM{i+1:06d}",
            "step": int(steps[i]),
            "amount": float(amounts[i]),
            "type_CASH_OUT": types[i] == "CASH_OUT",
            "type_DEBIT": types[i] == "DEBIT",
            "type_PAYMENT": types[i] == "PAYMENT",
            "type_TRANSFER": types[i] == "TRANSFER"
        }
        for i in range(number)
    ]

    return {
        "generated_transactions": number,
        "transactions": transactions
        }
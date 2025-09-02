from fastapi import FastAPI, Query
from pydantic import BaseModel
import joblib, json
import pandas as pd
import numpy as np
import os
from fastapi.middleware.cors import CORSMiddleware

# CORS settings
origins = [
    "http://127.0.0.1:4200",
    "http://localhost:4200",
]

# Author: Hugo Guerrero
# Date: August 2024
# Description: API for fraud detection using a pre-trained XGBClassifier model.


# Initialize FastAPI app
BASE_DIR = os.path.join(os.path.dirname(__file__), 'modelo')

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    TransactionID: str
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrg: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int
    isFlaggedFraud: int

class TransactioninBatch(BaseModel):
    transactions: int
    transactions: list[Transaction]


@app.post("/predict")
def predict(transaction: Transaction):
    
    tx_raw = transaction.model_dump()

    df = transform_to_features([tx_raw])
    features_row = df.iloc[0].to_dict()

    # prediction for single
    y_proba = model.predict_proba(df)[:, 1][0]
    y_pred = int(y_proba >= THRESHOLD)

    return {
        "transaction_raw": tx_raw,
        "transaction_features": features_row,
        "probability": float(y_proba),
        "prediction": y_pred,
        "threshold": THRESHOLD,
        "metadata": {
            "model_version": metadata["model_version"],
            "model_type": metadata["model_type"],
            "model_name": metadata["model_name"],
        },
    }

# Pipeline to transform raw transaction data to model features
def transform_to_features(tx_list: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(tx_list)

    # Drop columns not used in the model
    drop_cols = [
        "TransactionID","nameOrig","nameDest",
        "oldbalanceOrg","newbalanceOrg","oldbalanceDest","newbalanceDest",
        "isFlaggedFraud","isFraud"
    ]

    # Drop only if they exist
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    # Ensure numeric types and handle missing values
    df["step"] = pd.to_numeric(df.get("step"), errors="coerce").fillna(0).astype(int)
    df["amount"] = pd.to_numeric(df.get("amount"), errors="coerce").fillna(0.0).astype(float)

    # One-hot
    if "type" in df.columns:
        df["type_CASH_OUT"] = df["type"].eq("CASH_OUT")
        df["type_DEBIT"]    = df["type"].eq("DEBIT")
        df["type_PAYMENT"]  = df["type"].eq("PAYMENT")
        df["type_TRANSFER"] = df["type"].eq("TRANSFER")
        df = df.drop(columns=["type"])

    # Add missing columns with default 0
    expected = ["step","amount","type_CASH_OUT","type_DEBIT","type_PAYMENT","type_TRANSFER"]
    for col in expected:
        if col not in df.columns:
            df[col] = 0

    # Ensure correct types
    for col in ["type_CASH_OUT","type_DEBIT","type_PAYMENT","type_TRANSFER"]:
        df[col] = df[col].astype(int)

    # Ensure correct column order
    df = df[["step","amount","type_CASH_OUT","type_DEBIT","type_PAYMENT","type_TRANSFER"]]
    return df

# Endpoint for batch predictions
@app.post("/predict_batch")
def predict_batch(transactions: TransactioninBatch):

    tx_list = transactions.model_dump()["transactions"]

    df = transform_to_features(tx_list)

    # prediction for batch
    y_proba = model.predict_proba(df)[:, 1]
    y_pred = (y_proba >= THRESHOLD).astype(int)

    results = []
    frauds = []

    for i, (tx, proba, pred) in enumerate(zip(tx_list, y_proba, y_pred)):
        features_row = df.iloc[i].to_dict()
        result = {
            "transaction_raw": tx,
            "transaction_features": features_row,
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

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Fraud Detection API is running!",
        "model_name": metadata["model_name"],
        "model_version": metadata["model_version"],
        "threshold": THRESHOLD
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Endpoint to generate simulated transactions
@app.get("/generate_transactions")
def generate_transactions(number: int = Query(10, description="Número de transacciones a generar")):
    steps = np.random.randint(1, 744, size=number)
    types = np.random.choice(["CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"], size=number)
    dest_Prefix = ["M", "C"]
    
    transactions = []
    for i in range(number):
        amount = float(np.round(np.random.uniform(0.0, 100000.0), 2))
        oldbalanceOrg = float(np.round(np.random.uniform(0.0, 100000.0), 2))
        newbalanceOrg = max(oldbalanceOrg - amount, 0.0)

        oldbalanceDest = float(np.round(np.random.uniform(0.0, 50000.0), 2)) if np.random.rand() > 0.7 else 0.0
        newbalanceDest = oldbalanceDest + amount if np.random.rand() > 0.5 else oldbalanceDest

        isFraud = int(np.random.choice([0, 1], p=[0.95, 0.05]))

        transactions.append({
            "TransactionID": f"SIM{i+1:06d}",
            "step": int(steps[i]),
            "type": types[i],
            "amount": amount,
            "nameOrig": f"C{np.random.randint(1000000, 9999999)}",
            "oldbalanceOrg": oldbalanceOrg,
            "newbalanceOrg": newbalanceOrg,
            "nameDest": f"{np.random.choice(dest_Prefix)}{np.random.randint(1000000, 9999999)}",
            "oldbalanceDest": oldbalanceDest,
            "newbalanceDest": newbalanceDest,
            "isFraud": isFraud,
            "isFlaggedFraud": 0         
        })
        
    return {
        "generated_transactions": number,
        "transactions": transactions
        }
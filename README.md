# Proyecto Fraud Detection API

## Objetivo
Construir un modelo de **machine learning** que detecte si una operación es fraudulenta, basado en las características de las transacciones.

## Descripción

### Requisitos previos
- Python 3.13+
- pip
- Virtualenv <small style="font-size: 0.8em;">*Recomendado.</small>

## ⚙️ Instalación
1. `git clone https://github.com/haguerrero/proyecto_fraudes.git`

2. Crear venv
`python3 -m venv v_fraud_model`

3. Dependencias
`pip install -r requirements`

4. Fraud Detection API

API para la detección de transacciones financieras con comportamientos fraudulentos, usando un modelo de Machine Learning construido con **FastAPI** y exponer el modelo como servicio

##### ▶️ Ejecutar el proyecto en local
```bash
uvicorn app_fraud:app --reload
```
Esto levantará la API en `http://127.0.0.1:8000`

## Uso de la API

## Detalles del modelo
- Algoritmo: `XGBClassifier`
- Dataset: [-Kaggle- Fraudulent Transactions Data](https://www.kaggle.com/datasets/chitwanmanchanda/fraudulent-transactions-data/data) 
- Features:
    - `amount`
    - `




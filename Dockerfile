# image base of python 3.13 slim
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# PORT where the app will run
EXPOSE 8000

CMD ["uvicorn", "app_fraud:app", "--host", "0.0.0.0", "--port", "8000"]


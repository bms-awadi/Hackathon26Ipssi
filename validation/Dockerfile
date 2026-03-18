FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn joblib pandas scikit-learn lazypredict
COPY . .
RUN python train.py 2>/dev/null || echo "Pas de dataset encore, modele ML désactivé"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
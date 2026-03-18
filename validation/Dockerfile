FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn joblib pandas scikit-learn lazypredict
COPY . .
RUN python train.py || echo "Pas de dataset encore, modele ML désactivé"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
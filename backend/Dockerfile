FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data
CMD ["sh", "-c", "python -m app.seed && gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 run:app"]

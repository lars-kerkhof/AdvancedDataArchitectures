FROM python:3.10-slim

WORKDIR /app
COPY requirements_pod.txt .
RUN pip install --no-cache-dir -r requirements_pod.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

FROM python:3.12-slim

WORKDIR /usr/src/myapp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]
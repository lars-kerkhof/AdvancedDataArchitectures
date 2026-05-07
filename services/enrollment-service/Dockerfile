FROM python:3.12.7-slim
WORKDIR /usr/src/myapp
COPY requirements_pod.txt .
RUN pip install --no-cache-dir -r requirements_pod.txt
COPY . .
EXPOSE 5000
ENV DB_URL=sqlite:///enrollment-service.db
CMD ["python3","app.py"]

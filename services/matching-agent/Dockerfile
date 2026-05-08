# Using python 3.12.7 slim image as the base image
FROM python:3.12.7-slim
# Defining working directory and copy the requirements file
WORKDIR /usr/src/myapp
# Copy requirements.txt to the working directory
COPY requirements.txt .
# Install required python packages
RUN pip install --no-cache-dir -r requirements.txt
# Copy all files to /usr/src/myapp in Docker container
COPY . .
# Expose the port
EXPOSE 5000
# Environment Variables
ENV DB_URL=sqlite:///user.db
ENV SECRET_KEY=key.txt
# Run the app
CMD ["python3","app.py"]

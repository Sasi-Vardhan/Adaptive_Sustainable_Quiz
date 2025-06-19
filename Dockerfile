FROM python:3.10-slim

# Add system packages including distutils
RUN apt-get update && \
    apt-get install -y python3-distutils gcc build-essential

# Set working directory
WORKDIR /app

# Copy all code
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

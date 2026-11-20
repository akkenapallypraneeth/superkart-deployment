# Lightweight Python image
FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# Install the dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and the serialized model
COPY . .

# The Flask API listens on port 7860
EXPOSE 7860

# Serve the app with gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:7860", "app:superkart_api"]

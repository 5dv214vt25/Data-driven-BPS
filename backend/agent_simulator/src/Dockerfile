# Use an official Python 3.9 slim base image
FROM python:3.9-slim

# environment variables for Python (optional)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Sworking directory
WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# (Optional) If app listens on a port, expose it
# EXPOSE 8000

# Note that this is not used when starting the container with an interactive shell, which
# we currently are done
CMD ["python3.9", "simulate.py"]

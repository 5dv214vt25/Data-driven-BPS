# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    APP_HOME=/app

# 3. Create and set the working directory
WORKDIR $APP_HOME

# 4. Install pip dependencies
#    Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Expose the port FastAPI will run on
EXPOSE 8080

# 7. Default command to run your app with Uvicorn
#    We bind to 0.0.0.0 so it’s reachable from outside the container
CMD ["uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

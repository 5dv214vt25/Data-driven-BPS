# delivery.Dockerfile
# Dockerfile for building the application for a production deployment

FROM python:3.9-slim

# Create a non-root user and group
RUN addgroup --system controllergroup && adduser --system --ingroup controllergroup controlleruser

WORKDIR /controller

COPY requirements.txt /controller/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy the rest of the app and fix permissions
COPY . /controller/
RUN chown -R controlleruser:controllergroup /controller

USER controlleruser

ENV MPLCONFIGDIR=/tmp/matplotlib

EXPOSE 8888
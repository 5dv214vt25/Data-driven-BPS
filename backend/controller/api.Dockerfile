# api.Dockerfile
# Dockerfile for the controller application

FROM python:3.9-slim

# Create a non-root user and group
RUN addgroup --system controllergroup && adduser --system --ingroup controllergroup controlleruser

WORKDIR /controller

COPY controller/requirements.txt /controller/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy the rest of the app and fix permissions
COPY controller /controller/
RUN chown -R controlleruser:controllergroup /controller

USER controlleruser

# Prevent matplotlib from trying to write to the home directory
ENV MPLCONFIGDIR=/tmp/matplotlib

EXPOSE 8888

# Placeholder CMD; actual command defined in compose-file
CMD ["echo", "hej"]
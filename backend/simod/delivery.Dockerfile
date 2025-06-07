# Stage 1: Base with Java 8
FROM openjdk:8 as base

# Stage 2: Python + Java
FROM python:3.9-slim

WORKDIR /simod/src

# Copy Java from base image
COPY --from=base /usr/local/openjdk-8 /usr/local/openjdk-8
ENV JAVA_HOME=/usr/local/openjdk-8
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install any dependencies (optional: if Java needs other libs, install here)
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /simod/
RUN pip install --no-cache-dir -r ../requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . /simod/

EXPOSE 6001

ENV PYTHONPATH=/simod/simod_src/src/

ENV MPLCONFIGDIR=/tmp/matplotlib

CMD ["/bin/bash"]
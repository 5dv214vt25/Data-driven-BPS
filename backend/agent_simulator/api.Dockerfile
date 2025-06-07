FROM python:3.9-slim

# Create a non-root user and group
RUN useradd -m -d /home/agentuser -s /bin/bash agentuser

# Set environment variables
ENV HOME=/home/agentuser \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /agent_simulator/src

# Copy only requirements to leverage Docker cache
COPY /agent_simulator/requirements.txt ../requirements.txt
# Install dependencies
RUN pip install --no-cache-dir -r ../requirements.txt \
	&& pip install --no-cache-dir gunicorn

COPY /agent_simulator/ /agent_simulator/

# Create writable directory and fix ownership
RUN mkdir -p /agent_simulator/pickle_resources && \
	chown -R agentuser:agentuser /agent_simulator

# Switch to non-root user
USER agentuser

ENV MPLCONFIGDIR=/tmp/matplotlib

EXPOSE 6002

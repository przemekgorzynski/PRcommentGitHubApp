FROM python:3.12-slim

ENV USER ShelterScanner

# Ensure we are running as root to perform setup tasks
USER root

# Create applicationuser
RUN groupadd $USER && useradd -g $USER  -M -s /sbin/nologin $USER

# Create directory for secrets and copy them
RUN mkdir /secrets
COPY secrets/github.pem /secrets/github.pem

RUN chown $USER:$USER /secrets/* && chmod 400 /secrets/*

# Copy app
WORKDIR /app
COPY app.py .
COPY requirements.txt .

RUN chown $USER:$USER /app/* && chmod 660 /app/app.py

# Install Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose app's port
EXPOSE 8000

# Switch to application user 
USER $USER

# Run app
ENTRYPOINT ["fastapi", "run"]
CMD ["/app/app.py", "--port", "8000"]

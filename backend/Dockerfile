FROM python:3.13-slim-bookworm

# Create non-root user
RUN groupadd -r sysuser && useradd -r -g sysuser sysuser

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd gcc postgresql-client libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install dev requirements (DEV ONLY)
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy other project files
COPY . .

# Set ownership and permissions
RUN chown -R sysuser:sysuser /usr/src/app && \
    chmod +x /usr/src/app/entrypoint.sh

# Switch to non-root user
USER sysuser

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
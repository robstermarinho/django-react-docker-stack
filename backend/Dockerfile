# pull Python  image
FROM python:3.13-slim-bookworm

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install app dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd gcc postgresql redis gnupg2 curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
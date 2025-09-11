# Django + React + Docker Fullstack Application

A full-stack web application built with Django (backend), React (frontend), PostgreSQL (database), and Nginx (reverse proxy), all containerized with Docker.

## Architecture

- **Backend**: Django REST API
- **Frontend**: React with Vite
- **Database**: PostgreSQL 17
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker
- Docker Compose

## Installation & Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd django-react-fullstack
```

2. Create environment file:
```bash
cp backend/.env.example backend/.env
```

3. Configure your environment variables in `backend/.env`

4. Build and start all services:
```bash
docker-compose up --build
```

5. For subsequent runs (without rebuilding):
```bash
docker-compose up
```

## Access URLs

- **Frontend (React)**: http://localhost:5174
- **Backend API (Django)**: http://localhost:8019
- **Nginx (Reverse Proxy)**: http://localhost:8018
- **Database (PostgreSQL)**: localhost:5418

## Development

### Backend (Django)
- API runs on port 8000 inside container, exposed on 8019
- Auto-reloads on code changes
- Access Django admin at http://localhost:8019/admin

### Frontend (React)
- Vite dev server runs on port 5173 inside container, exposed on 5174
- Hot module replacement enabled
- Auto-reloads on code changes

### Database
- PostgreSQL 17
- Data persists in Docker volume `postgres_data`
- Access via localhost:5418

## Useful Commands

```bash
# Stop all services
docker-compose down

# View logs
docker-compose logs [service-name]

# Rebuild specific service
docker-compose build [service-name]

# Run Django migrations
docker-compose exec api python manage.py migrate

# Create Django superuser
docker-compose exec api python manage.py createsuperuser

# Access container shell
docker-compose exec [service-name] /bin/bash
```

## Services

- **api**: Django backend application
- **web**: React frontend application  
- **db**: PostgreSQL database
- **nginx**: Nginx reverse proxy
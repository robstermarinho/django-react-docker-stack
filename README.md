# Django + React Fullstack Application

Complete stack with Django backend, React frontend, PostgreSQL and Nginx.

## 🛠 Tech Stack

- **Backend:** Django 5.2 + PostgreSQL
- **Frontend:** React + Vite + TypeScript (Node.js 22)
- **Proxy:** Nginx
- **Containerization:** Docker + Docker Compose
- **Dependency Management:** Poetry + Docker

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Poetry
- Node.js 22+

### Step-by-Step Setup

1. **Clone the repository:**
```bash
git clone <repo-url>
cd django-react-fullstack
```

2. **Start the application:**
```bash
docker compose up --build
```


3. **Create a Django superuser (optional):**
```bash
docker compose exec api python manage.py createsuperuser
```


## 📱 Access Points

- **Frontend (Vite):** http://localhost:5174
- **Backend (via Nginx):** http://localhost:8018  
- **PostgreSQL:** localhost:5418


## 🐳 Docker

### Useful commands:

```bash
# View logs
docker compose logs -f api

# Execute commands in container
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser

# Rebuild a specific service
docker compose up --build api

# Stop everything
docker compose down
```


## 🔧 Available Make Commands

### Development Environment
```bash
make help              # Show all available commands
make up                # Start development environment
make up-d              # Start environment (detached mode)
make clean             # Remove containers and volumes
```

### Dependency Management (Poetry)
```bash
make poetry-install           # Install dependencies locally
make poetry-add PACKAGE=name  # Add production dependency
make poetry-add-dev PACKAGE=name # Add development dependency
make poetry-update            # Update all dependencies
make poetry-remove PACKAGE=name # Remove dependency
make poetry-show-outdated     # Show outdated dependencies
make poetry-export            # Export to requirements.txt
make poetry-shell             # Open Poetry shell
```

### Development
```bash
make backend-shell       # Shell in backend container
make backend-restart     # Restart backend container
make frontend-install    # Install frontend dependencies
make frontend-build      # Build frontend
make frontend-restart    # Restart frontend container
make test               # Run tests
make lint               # Run local linting
make format             # Format local code
```

## ⚙️ Services Architecture

- **nginx** (8018:80) - Reverse proxy, serves static files
- **api** (Django) - Backend API (internal only)
- **web** (5174:5173) - React Frontend with Vite
- **db** (5418:5432) - PostgreSQL with persistent volumes
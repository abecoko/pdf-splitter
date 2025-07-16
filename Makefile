.PHONY: help build run dev test clean logs stop restart

# Default target
help:
	@echo "PDF Splitter - Available commands:"
	@echo "  build     Build production Docker images"
	@echo "  run       Run production environment"
	@echo "  dev       Run development environment with hot reload"
	@echo "  test      Run backend tests"
	@echo "  clean     Clean up containers and images"
	@echo "  logs      Show logs from all services"
	@echo "  stop      Stop all services"
	@echo "  restart   Restart all services"

# Build production images
build:
	@echo "Building production Docker images..."
	docker-compose build

# Run production environment
run: build
	@echo "Starting production environment..."
	docker-compose up -d
	@echo "Application available at http://localhost:3000"
	@echo "Backend API available at http://localhost:3000/api"

# Run development environment
dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Frontend available at http://localhost:3000"
	@echo "Backend API available at http://localhost:8000"

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v

# View logs
logs:
	docker-compose logs -f

# Stop services
stop:
	@echo "Stopping all services..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Restart services
restart: stop run

# Clean up
clean: stop
	@echo "Cleaning up containers and images..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker-compose -f docker-compose.dev.yml down --rmi all --volumes --remove-orphans
	docker system prune -f

# Install dependencies for local development
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run backend locally
run-backend:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally
run-frontend:
	cd frontend && npm run dev

# Format code
format:
	cd backend && python -m black . && python -m isort .
	cd frontend && npm run lint

# Check code quality
lint:
	cd backend && python -m black --check . && python -m isort --check-only .
	cd frontend && npm run lint

# Check service status
status:
	@echo "Checking service status..."
	docker-compose ps
	@echo "\nChecking container logs..."
	docker-compose logs --tail=20

# Debug connectivity
debug:
	@echo "Debugging connectivity..."
	@echo "Testing backend health..."
	curl -f http://localhost:3000/api/health || echo "Backend not accessible"
	@echo "\nTesting frontend..."
	curl -I http://localhost:3000 || echo "Frontend not accessible"
	@echo "\nContainer status:"
	docker-compose ps
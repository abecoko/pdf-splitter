#!/bin/bash
set -e

echo "🚀 Starting PDF Splitter Application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if ports are available
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use. Please free the port or modify docker-compose.yml"
        return 1
    fi
    return 0
}

# Check port 3000
if ! check_port 3000; then
    echo "Suggestion: Edit docker-compose.yml and change '3000:80' to '8080:80'"
    echo "Then access the app at http://localhost:8080"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build --no-cache

echo "🏃 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS - Waiting for backend..."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Backend failed to start properly. Showing logs:"
    docker-compose logs backend
    exit 1
fi

# Check frontend
if curl -I http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible!"
else
    echo "❌ Frontend is not accessible. Showing logs:"
    docker-compose logs frontend
    exit 1
fi

echo ""
echo "🎉 PDF Splitter is now running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:3000/api"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
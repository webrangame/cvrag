#!/bin/bash

echo "🚀 Starting RAG Application..."
echo "================================"
echo ""
echo "Building and starting Docker containers..."
docker-compose up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "✓ Application is running!"
echo ""
echo "Access the application at: http://localhost:8000"
echo "MySQL is available at: localhost:3306"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""

# Display running containers
echo "Running containers:"
docker-compose ps


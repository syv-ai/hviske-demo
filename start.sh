#!/bin/bash

# Tale Transskription Service Startup Script
# This script helps you start the transcription service easily

set -e

echo "🎙️  Tale Transskription Service Startup"
echo "====================================="

# Function to check if docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        echo "   Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

# Function to check if docker-compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        echo "   Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Function to check GPU support
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        echo "✅ NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    else
        echo "⚠️  No NVIDIA GPU detected. Service will run on CPU (slower performance)."
    fi
}

# Function to check if nvidia-docker is installed
check_nvidia_docker() {
    if docker info | grep -q "nvidia"; then
        echo "✅ NVIDIA Docker support detected"
    else
        echo "⚠️  NVIDIA Docker support not detected. GPU acceleration may not work."
        echo "   Install NVIDIA Container Toolkit: https://github.com/NVIDIA/nvidia-docker"
    fi
}

# Main startup function
start_service() {
    echo ""
    echo "🚀 Starting Tale Transskription Service..."
    echo ""
    
    # Check if port 8000 is available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port 8000 is already in use. Please stop the service using it first."
        echo "   You can check what's using port 8000 with: lsof -i :8000"
        exit 1
    fi
    
    # Build and start the service
    echo "🔨 Building Docker image..."
    docker-compose build
    
    echo "🏃 Starting service..."
    docker-compose up -d
    
    echo ""
    echo "✅ Service started successfully!"
    echo ""
    echo "📱 Web Interface: http://localhost:8000"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo "📋 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📝 To view logs: docker-compose logs -f"
    echo "🛑 To stop service: docker-compose down"
    echo ""
    
    # Wait for service to be ready
    echo "⏳ Waiting for service to be ready..."
    timeout=120
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Service is ready!"
            break
        fi
        echo -n "."
        sleep 2
        counter=$((counter + 2))
    done
    
    if [ $counter -ge $timeout ]; then
        echo ""
        echo "⚠️  Service is taking longer than expected to start."
        echo "   Check logs with: docker-compose logs"
    fi
}

# Main script execution
main() {
    case "${1:-start}" in
        start)
            check_docker
            check_docker_compose
            check_gpu
            check_nvidia_docker
            start_service
            ;;
        stop)
            echo "🛑 Stopping Tale Transskription Service..."
            docker-compose down
            echo "✅ Service stopped."
            ;;
        restart)
            echo "🔄 Restarting Tale Transskription Service..."
            docker-compose down
            docker-compose up -d
            echo "✅ Service restarted."
            ;;
        logs)
            echo "📝 Showing service logs..."
            docker-compose logs -f
            ;;
        status)
            echo "📊 Service Status:"
            docker-compose ps
            echo ""
            echo "Health Check:"
            curl -s http://localhost:8000/health 2>/dev/null || echo "Service not responding"
            ;;
        build)
            echo "🔨 Building Docker image..."
            docker-compose build --no-cache
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|logs|status|build}"
            echo ""
            echo "Commands:"
            echo "  start   - Start the transcription service (default)"
            echo "  stop    - Stop the transcription service"
            echo "  restart - Restart the transcription service"
            echo "  logs    - Show service logs"
            echo "  status  - Show service status"
            echo "  build   - Rebuild Docker image"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 
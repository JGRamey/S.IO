#!/bin/bash

# S.IO Docker Setup Script
# Usage: ./docker-setup.sh [command]

set -e

PROJECT_NAME="s-io"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    fi
}

start_services() {
    print_status "Starting S.IO services..."
    docker-compose up -d
    
    print_status "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    if docker-compose ps | grep -q "healthy"; then
        print_success "All services are running!"
        show_status
    else
        print_warning "Some services may still be starting. Run './docker-setup.sh status' to check."
    fi
}

stop_services() {
    print_status "Stopping S.IO services..."
    docker-compose down
    print_success "Services stopped."
}

restart_services() {
    print_status "Restarting S.IO services..."
    docker-compose restart
    print_success "Services restarted."
}

show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Available endpoints:"
    echo "  PostgreSQL: localhost:5432 (user: postgres, password: postgres, db: yggdrasil)"
    echo "  Qdrant: http://localhost:6333"
    echo "  S.IO App: http://localhost:8000"
}

show_logs() {
    if [ -n "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f
    fi
}

rebuild() {
    print_status "Rebuilding S.IO application..."
    docker-compose build --no-cache s-io
    print_success "Rebuild complete."
}

clean() {
    print_warning "This will remove all containers and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup complete."
    else
        print_status "Cleanup cancelled."
    fi
}

case "$1" in
    start)
        check_docker
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    rebuild)
        check_docker
        rebuild
        ;;
    clean)
        clean
        ;;
    *)
        echo "S.IO Docker Setup Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|rebuild|clean}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services (PostgreSQL, Qdrant, S.IO)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status and endpoints"
        echo "  logs     - Show logs (optionally specify service name)"
        echo "  rebuild  - Rebuild the S.IO application container"
        echo "  clean    - Remove all containers and volumes"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs postgres"
        echo "  $0 status"
        exit 1
        ;;
esac

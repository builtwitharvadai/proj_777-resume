#!/bin/bash

# Development environment setup script
# Initializes development environment, creates .env file, runs migrations, and starts services

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Error handling
handle_error() {
    log_error "Script failed at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Check if required commands are available
check_requirements() {
    log_info "Checking requirements..."

    local missing_requirements=0

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        missing_requirements=1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        missing_requirements=1
    fi

    if [ $missing_requirements -eq 1 ]; then
        exit 1
    fi

    log_info "All requirements satisfied."
}

# Create .env file from template
create_env_file() {
    log_info "Setting up environment file..."

    if [ -f ".env" ]; then
        log_warning ".env file already exists. Skipping creation."
        read -p "Do you want to overwrite it? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing .env file."
            return
        fi
    fi

    if [ ! -f ".env.example" ]; then
        log_error ".env.example file not found."
        exit 1
    fi

    cp .env.example .env
    log_info ".env file created successfully from .env.example"

    # Update default values for development
    if command -v sed &> /dev/null; then
        sed -i.bak 's/DEBUG=False/DEBUG=True/' .env
        sed -i.bak 's/ENVIRONMENT=production/ENVIRONMENT=development/' .env
        sed -i.bak 's|DATABASE_URL=.*|DATABASE_URL=postgresql://resume_user:resume_password@localhost:5432/resume_db|' .env
        sed -i.bak 's|REDIS_URL=.*|REDIS_URL=redis://localhost:6379/0|' .env
        rm -f .env.bak
        log_info "Updated .env with development defaults."
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    mkdir -p logs
    mkdir -p uploads

    log_info "Directories created successfully."
}

# Start Docker services
start_services() {
    log_info "Starting Docker services..."

    if docker compose version &> /dev/null; then
        docker compose up -d db redis
    else
        docker-compose up -d db redis
    fi

    log_info "Waiting for services to be ready..."
    sleep 10

    log_info "Docker services started successfully."
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    if docker compose version &> /dev/null; then
        docker compose run --rm backend alembic upgrade head || {
            log_warning "Failed to run migrations via Docker. Attempting local execution..."
            if command -v alembic &> /dev/null; then
                alembic upgrade head
            else
                log_error "Alembic not found. Please install dependencies or use Docker."
                exit 1
            fi
        }
    else
        docker-compose run --rm backend alembic upgrade head || {
            log_warning "Failed to run migrations via Docker. Attempting local execution..."
            if command -v alembic &> /dev/null; then
                alembic upgrade head
            else
                log_error "Alembic not found. Please install dependencies or use Docker."
                exit 1
            fi
        }
    fi

    log_info "Database migrations completed successfully."
}

# Start all services
start_all_services() {
    log_info "Starting all application services..."

    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    log_info "All services started successfully."
}

# Display service status
show_status() {
    log_info "Service status:"

    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi

    echo ""
    log_info "Development environment is ready!"
    echo ""
    log_info "Backend API: http://localhost:8000"
    log_info "Frontend: http://localhost:3000"
    log_info "API Documentation: http://localhost:8000/docs"
    echo ""
    log_info "To view logs, run: docker compose logs -f"
    log_info "To stop services, run: docker compose down"
}

# Main execution
main() {
    log_info "Starting development environment setup..."
    echo ""

    check_requirements
    create_env_file
    create_directories
    start_services
    run_migrations
    start_all_services
    show_status

    log_info "Setup completed successfully!"
}

# Run main function
main

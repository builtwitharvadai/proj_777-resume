#!/bin/bash

# Database reset script for development
# Resets database, runs migrations, and optionally seeds with test data

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

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Confirm destructive action
confirm_reset() {
    log_warning "This will DELETE all data in the database and reset it to a clean state."
    read -p "Are you sure you want to continue? (yes/N) " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Database reset cancelled."
        exit 0
    fi
}

# Stop backend service
stop_backend() {
    log_info "Stopping backend service..."

    if docker compose version &> /dev/null; then
        docker compose stop backend || true
    else
        docker-compose stop backend || true
    fi

    log_info "Backend service stopped."
}

# Drop and recreate database
reset_database() {
    log_info "Resetting database..."

    # Get database container name
    local db_container
    if docker compose version &> /dev/null; then
        db_container=$(docker compose ps -q db)
    else
        db_container=$(docker-compose ps -q db)
    fi

    if [ -z "$db_container" ]; then
        log_error "Database container not found. Please start services first."
        exit 1
    fi

    # Drop all connections and drop database
    docker exec -i "$db_container" psql -U resume_user -d postgres <<-EOSQL || {
        log_warning "Failed to drop database. It may not exist yet."
    }
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'resume_db'
        AND pid <> pg_backend_pid();

        DROP DATABASE IF EXISTS resume_db;
EOSQL

    # Create database
    docker exec -i "$db_container" psql -U resume_user -d postgres <<-EOSQL
        CREATE DATABASE resume_db;
        GRANT ALL PRIVILEGES ON DATABASE resume_db TO resume_user;
EOSQL

    log_info "Database reset successfully."
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    if docker compose version &> /dev/null; then
        docker compose run --rm backend alembic upgrade head
    else
        docker-compose run --rm backend alembic upgrade head
    fi

    log_info "Migrations completed successfully."
}

# Seed database with test data
seed_database() {
    log_info "Would you like to seed the database with test data?"
    read -p "Seed database? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Seeding database with test data..."

        # Create test data using Python script
        if docker compose version &> /dev/null; then
            docker compose run --rm backend python -c "
import asyncio
from src.auth.security import hash_password
from src.database.connection import AsyncSessionLocal
from src.database.models.user import User
from datetime import datetime

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Create test users
        test_users = [
            User(
                email='admin@example.com',
                hashed_password=hash_password('admin123'),
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            User(
                email='user@example.com',
                hashed_password=hash_password('user123'),
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            User(
                email='test@example.com',
                hashed_password=hash_password('test123'),
                email_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]

        for user in test_users:
            session.add(user)

        await session.commit()
        print('Test data seeded successfully!')

asyncio.run(seed_data())
" || log_warning "Failed to seed database. Continuing..."
        else
            docker-compose run --rm backend python -c "
import asyncio
from src.auth.security import hash_password
from src.database.connection import AsyncSessionLocal
from src.database.models.user import User
from datetime import datetime

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Create test users
        test_users = [
            User(
                email='admin@example.com',
                hashed_password=hash_password('admin123'),
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            User(
                email='user@example.com',
                hashed_password=hash_password('user123'),
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            User(
                email='test@example.com',
                hashed_password=hash_password('test123'),
                email_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]

        for user in test_users:
            session.add(user)

        await session.commit()
        print('Test data seeded successfully!')

asyncio.run(seed_data())
" || log_warning "Failed to seed database. Continuing..."
        fi

        log_info "Test users created:"
        echo "  - admin@example.com / admin123 (verified)"
        echo "  - user@example.com / user123 (verified)"
        echo "  - test@example.com / test123 (not verified)"
    else
        log_info "Skipping database seeding."
    fi
}

# Start backend service
start_backend() {
    log_info "Starting backend service..."

    if docker compose version &> /dev/null; then
        docker compose up -d backend
    else
        docker-compose up -d backend
    fi

    log_info "Backend service started."
}

# Display completion message
show_completion() {
    log_info "Database reset completed successfully!"
    echo ""
    log_info "Database has been reset and migrations applied."
    log_info "Backend API: http://localhost:8000"
    log_info "API Documentation: http://localhost:8000/docs"
}

# Main execution
main() {
    log_info "Starting database reset..."
    echo ""

    check_docker
    confirm_reset
    stop_backend
    reset_database
    run_migrations
    seed_database
    start_backend
    show_completion

    log_info "Database reset completed!"
}

# Run main function
main

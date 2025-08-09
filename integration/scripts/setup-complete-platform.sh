#!/bin/bash

# =============================================================================
# MotoGP Analytics Platform - Complete Setup Script
# =============================================================================
# This script sets up the complete MotoGP Analytics platform by cloning all
# repositories and setting up the integrated development environment.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PLATFORM_DIR="motogp-analytics-platform"
REPOS=(
    "motogp-data-science"
    "motogp-analytics-api"
    "motogp-dashboard"
    "motogp-infrastructure"
)
GITHUB_USER="diogo-costa-silva"

# Functions
print_header() {
    echo -e "\n${BLUE}🏎️  MotoGP Analytics Platform Setup${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

print_step() {
    echo -e "${YELLOW}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is required but not installed."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

setup_directory() {
    print_step "Setting up platform directory..."
    
    if [ -d "$PLATFORM_DIR" ]; then
        echo -e "${YELLOW}⚠️  Directory $PLATFORM_DIR already exists. Remove it? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf "$PLATFORM_DIR"
        else
            print_error "Setup cancelled."
            exit 1
        fi
    fi
    
    mkdir -p "$PLATFORM_DIR"
    cd "$PLATFORM_DIR"
    
    print_success "Platform directory created: $PLATFORM_DIR"
}

clone_repositories() {
    print_step "Cloning all MotoGP Analytics repositories..."
    
    for repo in "${REPOS[@]}"; do
        echo -e "  📥 Cloning ${repo}..."
        if git clone "https://github.com/${GITHUB_USER}/${repo}.git"; then
            print_success "  ✅ ${repo} cloned successfully"
        else
            print_error "  ❌ Failed to clone ${repo}"
            exit 1
        fi
    done
    
    print_success "All repositories cloned successfully"
}

setup_environment() {
    print_step "Setting up environment configuration..."
    
    # Copy environment template from main repo
    if [ -f "motogp-analytics/integration/.env.template" ]; then
        cp "motogp-analytics/integration/.env.template" .env
        print_success "Environment template copied to .env"
        echo -e "${YELLOW}⚠️  Please edit .env file with your specific configuration${NC}"
    else
        print_error "Environment template not found"
    fi
}

setup_python_environment() {
    print_step "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install requirements for each component
    for repo in "${REPOS[@]}"; do
        if [ -f "$repo/pyproject.toml" ]; then
            echo "  📦 Installing dependencies for $repo..."
            cd "$repo"
            pip install -e ".[dev]"
            cd ..
        fi
    done
    
    print_success "Python environment setup completed"
}

setup_infrastructure() {
    print_step "Setting up infrastructure components..."
    
    cd motogp-infrastructure
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    # Create Docker networks if they don't exist
    docker network create motogp-network 2>/dev/null || true
    
    print_success "Infrastructure setup completed"
    cd ..
}

start_platform() {
    print_step "Starting the platform..."
    
    cd motogp-infrastructure
    
    # Start the platform using docker-compose
    if docker-compose up -d; then
        print_success "Platform started successfully"
        
        echo -e "\n${GREEN}🎉 MotoGP Analytics Platform is now running!${NC}"
        echo -e "\n📊 Access points:"
        echo -e "   • API Documentation: ${BLUE}http://localhost:8000/docs${NC}"
        echo -e "   • Interactive Dashboard: ${BLUE}http://localhost:8501${NC}"
        echo -e "   • Grafana Monitoring: ${BLUE}http://localhost:3000${NC}"
        echo -e "   • Prometheus Metrics: ${BLUE}http://localhost:9090${NC}"
        
        echo -e "\n🔧 Useful commands:"
        echo -e "   • Health check: ${YELLOW}./scripts/health-check.sh${NC}"
        echo -e "   • View logs: ${YELLOW}docker-compose logs -f${NC}"
        echo -e "   • Stop platform: ${YELLOW}docker-compose down${NC}"
        
    else
        print_error "Failed to start platform"
        exit 1
    fi
    
    cd ..
}

run_health_check() {
    print_step "Running platform health check..."
    
    cd motogp-infrastructure
    sleep 30  # Wait for services to start
    
    if ./scripts/health-check.sh; then
        print_success "All services are healthy"
    else
        echo -e "${YELLOW}⚠️  Some services may still be starting up${NC}"
        echo -e "   Run './scripts/health-check.sh' again in a few minutes"
    fi
    
    cd ..
}

# Main execution
main() {
    print_header
    
    check_prerequisites
    setup_directory
    clone_repositories
    setup_environment
    setup_python_environment
    setup_infrastructure
    start_platform
    run_health_check
    
    echo -e "\n${GREEN}🚀 Setup completed successfully!${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo -e "1. Edit .env file with your configuration"
    echo -e "2. Access the dashboard at http://localhost:8501"
    echo -e "3. Explore the API at http://localhost:8000/docs"
    echo -e "4. Check Jupyter notebooks in motogp-data-science/"
    echo -e "\n${BLUE}For development:${NC}"
    echo -e "• Each repository has its own README with specific instructions"
    echo -e "• Use 'docker-compose logs -f' to monitor all services"
    echo -e "• Individual services can be developed independently"
}

# Error handling
trap 'print_error "Setup failed. Check the error messages above."; exit 1' ERR

# Run main function
main "$@"
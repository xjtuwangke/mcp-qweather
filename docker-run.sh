#!/bin/bash
# =============================================================================
# MCP Weather Docker Run Script
# =============================================================================
# This script runs the MCP Weather server in a Docker container.
#
# SECRETS INJECTION OPTIONS:
#
# Option 1: Mount secret file directly (RECOMMENDED for local development)
#   - Mount your private key file to /run/secrets/private_key.pem
#   - Set environment variables for API configuration
#
# Option 2: Use .env file with docker-compose
#   - Copy .env.example to .env and fill in your values
#   - Use docker-compose up
#
# Option 3: Inline environment variables (least secure)
#   - Pass secrets directly via -e flags (not recommended for production)
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# CONFIGURATION
# =============================================================================
# These values MUST be set before running the container
# You can set them via environment variables or replace ${VARIABLE} with actual values

REQUIRED_VARS=(
    "QWEATHER_API_HOST"
    "KEY_ID"
    "PROJECT_ID"
)

# Path to your private key (mounted into container at /run/secrets/private_key.pem)
PRIVATE_KEY_PATH="${PRIVATE_KEY_PATH:-./keys/ed25519-private.pem}"

# =============================================================================
# FUNCTIONS
# =============================================================================

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Run MCP Weather server in Docker container"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -d, --detach           Run container in detached mode"
    echo "  -p, --port PORT        Host port to expose (default: 8000)"
    echo "  --check-env            Check if required environment variables are set"
    echo ""
    echo ""
    echo "SECRETS INJECTION:"
    echo "  The private key is mounted as a Docker secret at /run/secrets/private_key.pem"
    echo "  Set the following environment variables:"
    echo "    QWEATHER_API_HOST    Your QWeather API host (e.g., https://xxx.qweatherapi.com)"
    echo "    KEY_ID               Your JWT key ID"
    echo "    PROJECT_ID           Your QWeather project ID"
    echo ""
    echo "  Example:"
    echo "    export QWEATHER_API_HOST=\"https://xxx.qweatherapi.com\""
    echo "    export KEY_ID=\"your-key-id\""
    echo "    export PROJECT_ID=\"your-project-id\""
    echo "    $0 --detach"
    echo ""
    echo "  Or use inline environment variables:"
    echo "    QWEATHER_API_HOST=\"https://xxx.qweatherapi.com\" \\"
    echo "    KEY_ID=\"your-key-id\" \\"
    echo "    PROJECT_ID=\"your-project-id\" \\"
    echo "    $0 --detach"
}

check_env() {
    echo "Checking required environment variables..."
    echo ""

    missing=0
    for var in "${REQUIRED_VARS[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo -e "${RED}✗${NC} $var is not set"
            missing=1
        else
            echo -e "${GREEN}✓${NC} $var is set"
        fi
    done
    echo ""

    # Check private key exists
    if [[ ! -f "$PRIVATE_KEY_PATH" ]]; then
        echo -e "${RED}✗${NC} Private key not found at $PRIVATE_KEY_PATH"
        missing=1
    else
        echo -e "${GREEN}✓${NC} Private key found at $PRIVATE_KEY_PATH"
    fi

    echo ""

    if [[ $missing -eq 1 ]]; then
        echo -e "${RED}Error: Missing required environment variables or files${NC}"
        return 1
    fi

    echo -e "${GREEN}All required variables are set!${NC}"
    return 0
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
        exit 1
    fi
}

build_image() {
    echo "Building Docker image..."
    docker build -t mcp-weather:latest .
}

# =============================================================================
# MAIN
# =============================================================================

DETACH=""
PORT="8000"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -d|--detach)
            DETACH="-d"
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --check-env)
            check_env
            exit $?
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

check_docker

# Check environment before running
if ! check_env 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}Warning: Some required environment variables are missing${NC}"
    echo "The container may fail to start."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build image if needed
if [[ ! -f "$SCRIPT_DIR/.dockerignore" ]] || ! docker image inspect mcp-weather:latest &> /dev/null; then
    build_image
fi

echo "Starting MCP Weather container on port $PORT..."

# Create secrets directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/.docker-secrets"

# Run container
docker run \
    --name mcp-weather \
    $DETACH \
    -p "${PORT}:8000" \
    -v "${SCRIPT_DIR}/${PRIVATE_KEY_PATH}:/run/secrets/private_key.pem:ro" \
    -e QWEATHER_API_HOST \
    -e KEY_ID \
    -e PROJECT_ID \
    -e PYTHONUNBUFFERED=1 \
    mcp-weather:latest

if [[ -z "$DETACH" ]]; then
    echo ""
    echo "Container is running. Press Ctrl+C to stop."
fi

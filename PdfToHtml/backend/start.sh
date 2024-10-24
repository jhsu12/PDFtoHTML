#!/bin/bash

# ==============================================
# (Run DEV Server Example): ENV=dev ./start.sh
# (Run PROD Server Example): ./start.sh
# =============================================

HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}
WORKER=${WORKER:-1}

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

if [ "$ENV" = "dev" ] || [ "$ENV" = "test" ]; then
    echo -e "============= ${YELLOW}Running Development Server${NC} ============="
    UVICORN_CMD="uvicorn app.main:app --host $HOST --port $PORT --workers $WORKER --reload"
else
    echo -e "============= ${RED}Running Production Server${NC} ============="
    UVICORN_CMD="uvicorn app.main:app --host $HOST --port $PORT --workers $WORKER"
fi

$UVICORN_CMD
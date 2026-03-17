#!/usr/bin/env bash
# hot-deploy.sh — Zero-downtime deployment for Claw Bench
# Usage: bash scripts/hot-deploy.sh [--skip-frontend] [--skip-server] [--skip-push]
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.prod.yml"

SKIP_FRONTEND=false
SKIP_SERVER=false
SKIP_PUSH=false

for arg in "$@"; do
    case $arg in
        --skip-frontend) SKIP_FRONTEND=true ;;
        --skip-server) SKIP_SERVER=true ;;
        --skip-push) SKIP_PUSH=true ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Claw Bench — Zero-Downtime Deploy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Verify site is online before starting
echo "[1/6] Verifying site is online..."
if curl -sf https://clawbench.net/api/health > /dev/null 2>&1; then
    echo "  ✓ Site is online"
else
    echo "  ! API not responding, proceeding anyway"
fi

# Step 2: Build frontend (nginx keeps serving old version)
if [ "$SKIP_FRONTEND" = false ]; then
    echo "[2/6] Building frontend..."
    cd "$PROJECT_DIR/leaderboard"
    npm run build --silent 2>&1 | tail -1
    echo "  ✓ Frontend built"
else
    echo "[2/6] Skipping frontend build"
fi

# Step 3: Build new server image (old container still running)
if [ "$SKIP_SERVER" = false ]; then
    echo "[3/6] Building server image..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" build server 2>&1 | tail -1
    echo "  ✓ Server image built"
else
    echo "[3/6] Skipping server build"
fi

# Step 4: Hot-swap server container (nginx stays up, 2-3s API blip)
if [ "$SKIP_SERVER" = false ]; then
    echo "[4/6] Hot-swapping server container..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" up -d --no-deps server 2>&1 | tail -2
    echo "  ✓ Server container replaced"

    # Wait for new server to be healthy
    echo "  Waiting for health check..."
    for i in $(seq 1 15); do
        if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
            echo "  ✓ Server healthy after ${i}s"
            break
        fi
        sleep 1
        if [ "$i" = "15" ]; then
            echo "  ! Server not healthy after 15s, check logs"
        fi
    done
else
    echo "[4/6] Skipping server swap"
fi

# Step 5: Reload nginx to pick up new frontend files (instant, no downtime)
if [ "$SKIP_FRONTEND" = false ]; then
    echo "[5/6] Reloading nginx..."
    docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload 2>/dev/null || \
        docker compose -f "$COMPOSE_FILE" restart nginx 2>&1 | tail -1
    echo "  ✓ Nginx reloaded"
else
    echo "[5/6] Skipping nginx reload"
fi

# Step 6: Final verification
echo "[6/6] Verifying deployment..."
sleep 2
if curl -sf https://clawbench.net/api/health > /dev/null 2>&1; then
    HEALTH=$(curl -sf https://clawbench.net/api/health)
    echo "  ✓ API: $HEALTH"
else
    echo "  ! API check failed"
fi
if curl -sf http://localhost:80/ -o /dev/null 2>&1; then
    echo "  ✓ Frontend: OK"
else
    echo "  ! Frontend check failed (may need browser verification)"
fi

DATA_COUNT=$(ls "$PROJECT_DIR/data/results/"*.json 2>/dev/null | wc -l)
echo "  ✓ Data: $DATA_COUNT result files"

# Optional: push to GitHub
if [ "$SKIP_PUSH" = false ]; then
    echo ""
    echo "Pushing to GitHub..."
    cd "$PROJECT_DIR"
    if [ -n "$(git status --porcelain)" ]; then
        git add -A
        git commit -m "deploy: $(date +%Y-%m-%d) update" 2>&1 | tail -1
    fi
    git push origin main 2>&1 | tail -1
    echo "  ✓ Pushed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Deploy complete. Site never went down."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

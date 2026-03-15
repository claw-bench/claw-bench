#!/usr/bin/env bash
# deploy.sh — Deploy Claw Bench to a server
# Usage: bash scripts/deploy.sh [setup|build|start|stop|ssl|status]
set -euo pipefail

DOMAIN="${DOMAIN:-clawbench.net}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.prod.yml"

cmd_setup() {
    echo "==> Installing dependencies..."
    apt-get update -qq
    apt-get install -y -qq docker.io docker-compose-v2 certbot python3-certbot-nginx
    systemctl enable docker
    systemctl start docker
    echo "    Done."
}

cmd_ssl() {
    echo "==> Obtaining SSL certificate for $DOMAIN..."
    mkdir -p /var/www/certbot
    certbot certonly --webroot -w /var/www/certbot \
        -d "$DOMAIN" -d "www.$DOMAIN" \
        --agree-tos --no-eff-email \
        --email "admin@$DOMAIN"

    # Copy certs to docker volume location
    SSL_DIR="$PROJECT_DIR/docker/ssl-certs"
    mkdir -p "$SSL_DIR"
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$SSL_DIR/"
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem "$SSL_DIR/"
    echo "    Certs copied to $SSL_DIR"
}

cmd_build() {
    echo "==> Building leaderboard frontend..."
    cd "$PROJECT_DIR/leaderboard"
    npm install
    npm run build
    echo "    Frontend built at leaderboard/out/"

    echo ""
    echo "==> Building Docker images..."
    docker compose -f "$COMPOSE_FILE" build
    echo "    Docker images ready."
}

cmd_start() {
    echo "==> Starting services..."
    docker compose -f "$COMPOSE_FILE" up -d
    echo "    Services started."
    cmd_status
}

cmd_stop() {
    echo "==> Stopping services..."
    docker compose -f "$COMPOSE_FILE" down
    echo "    Services stopped."
}

cmd_status() {
    echo "==> Service status:"
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    echo "==> Health check:"
    curl -sf http://localhost:8000/api/health 2>/dev/null && echo "  API: OK" || echo "  API: DOWN"
    curl -sf http://localhost:80/ -o /dev/null 2>/dev/null && echo "  Web: OK" || echo "  Web: DOWN"
}

case "${1:-help}" in
    setup)  cmd_setup ;;
    ssl)    cmd_ssl ;;
    build)  cmd_build ;;
    start)  cmd_start ;;
    stop)   cmd_stop ;;
    status) cmd_status ;;
    *)
        echo "Usage: $0 {setup|ssl|build|start|stop|status}"
        echo ""
        echo "  setup  — Install Docker + Certbot on a fresh server"
        echo "  ssl    — Obtain Let's Encrypt SSL certificate"
        echo "  build  — Build frontend + Docker images"
        echo "  start  — Start all services"
        echo "  stop   — Stop all services"
        echo "  status — Check service status"
        ;;
esac

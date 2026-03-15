#!/usr/bin/env bash
# Setup script for xdom-017-travel-itinerary
# Creates workspace with flight, hotel, and meeting data.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/flight_booking.json" "$WORKSPACE/flight_booking.json"
cp "$TASK_DIR/environment/data/hotel_booking.json" "$WORKSPACE/hotel_booking.json"
cp "$TASK_DIR/environment/data/meetings.json" "$WORKSPACE/meetings.json"
echo "Workspace ready with flight, hotel, and meeting data"

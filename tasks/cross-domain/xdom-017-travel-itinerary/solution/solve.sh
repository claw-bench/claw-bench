#!/usr/bin/env bash
# Oracle solution for xdom-017-travel-itinerary
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

with open('$WORKSPACE/flight_booking.json') as f:
    flights = json.load(f)
with open('$WORKSPACE/hotel_booking.json') as f:
    hotel = json.load(f)
with open('$WORKSPACE/meetings.json') as f:
    meetings = json.load(f)

itinerary = {
    'traveler': 'Business Trip to New York',
    'dates': '2026-03-25 to 2026-03-27',
    'days': [
        {
            'date': '2026-03-25',
            'label': 'Day 1 - Travel',
            'events': [
                {'time': '08:00', 'type': 'flight', 'description': 'Depart SFO → JFK (UA-1234), arrive 16:30'},
                {'time': '17:00', 'type': 'hotel', 'description': f\"Check in at {hotel['hotel']} ({hotel['confirmation']})\"}
            ]
        },
        {
            'date': '2026-03-26',
            'label': 'Day 2 - Meetings',
            'events': [
                {'time': '09:00', 'type': 'meeting', 'description': 'Client kickoff meeting at Client HQ - 350 5th Ave (2h)'},
                {'time': '14:00', 'type': 'meeting', 'description': 'Product demo at Client HQ - 350 5th Ave (1h)'},
                {'time': '19:00', 'type': 'meeting', 'description': 'Partnership dinner at Nobu Restaurant, 195 Broadway (2h)'}
            ]
        },
        {
            'date': '2026-03-27',
            'label': 'Day 3 - Return',
            'events': [
                {'time': '12:00', 'type': 'hotel', 'description': f\"Check out from {hotel['hotel']}\"},
                {'time': '18:00', 'type': 'flight', 'description': 'Depart JFK → SFO (UA-5678), arrive 21:30'}
            ]
        }
    ],
    'total_meetings': 3,
    'total_days': 3
}

with open('$WORKSPACE/itinerary.json', 'w') as f:
    json.dump(itinerary, f, indent=2)
"

echo "Solution written to $WORKSPACE/itinerary.json"

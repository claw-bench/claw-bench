# Task: Build Business Travel Itinerary

You are given three source files containing travel booking and meeting information. Compile them into a comprehensive day-by-day travel itinerary.

## Source Files

- `workspace/flight_booking.json` - outbound and return flight details
- `workspace/hotel_booking.json` - hotel reservation details
- `workspace/meetings.json` - list of scheduled meetings

## Requirements

1. Read all three source files.
2. Produce `workspace/itinerary.json` with the following structure:

### Fields

- `traveler`: a descriptive title like `"Business Trip to <city>"`
- `dates`: the trip date range in format `"YYYY-MM-DD to YYYY-MM-DD"` (from outbound flight date to return flight date)
- `days`: a list of day objects, one per day of the trip, each with:
  - `date`: the date in `YYYY-MM-DD` format
  - `label`: a description like `"Day 1 - Travel"`, `"Day 2 - Meetings"`, `"Day 3 - Return"`
  - `events`: a list of events for that day, each with:
    - `time`: the event time in `HH:MM` format
    - `type`: one of `"flight"`, `"hotel"`, or `"meeting"`
    - `description`: a human-readable description including key details (flight numbers, hotel name, meeting title, location, duration)
- `total_meetings`: the total number of meetings
- `total_days`: the total number of days in the trip

### Guidelines

- Day 1 (travel day): include the outbound flight and hotel check-in (estimate check-in ~30 min after arrival)
- Day 2 (meeting day): include all meetings sorted by time
- Day 3 (return day): include hotel check-out (at noon) and the return flight
- Include flight numbers in flight event descriptions
- Include the hotel confirmation number in at least one hotel event description
- Include meeting duration in meeting descriptions (e.g., "2h" for 120 minutes)

## Output

Save the result to `workspace/itinerary.json`.

# Task: Handle Timezone Conversion

You are given a calendar file at `workspace/calendar.json` containing 6 meetings with times in **UTC**.

Convert all meeting times from UTC to **US/Pacific** (PDT, which is UTC-7 in March 2026).

Each meeting has `start_time` and `end_time` fields in `"HH:MM"` format. Update these to reflect Pacific Daylight Time. If a time conversion causes the time to cross midnight backward, adjust the `date` field accordingly.

Add a `"timezone"` field set to `"US/Pacific"` to each meeting.

## Output

Write the converted calendar to `workspace/converted_calendar.json` with the same structure as the input.

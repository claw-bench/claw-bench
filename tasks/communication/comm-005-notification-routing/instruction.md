# Task: Notification Routing

You are given notifications and user preferences. Route each notification to the correct channels.

## Requirements

1. Read `workspace/notifications.json` — an array of notification objects with `id`, `user`, `type` (one of: `alert`, `update`, `reminder`, `promotion`), `title`, and `message`.
2. Read `workspace/preferences.json` — an object keyed by user, where each value maps notification types to an array of channels (e.g., `["email", "sms"]`). There is also a `"default"` key for users not listed.
3. For each notification, look up the user's preferences for that notification type. If the user is not in preferences, use the `"default"` entry.
4. Produce `workspace/routed.json` — an array of routing objects with: `notification_id`, `user`, `type`, `channels` (array of channels), `title`, `message`.
5. Sort the output by `notification_id`.

## Output

Save the routed notifications to `workspace/routed.json`.

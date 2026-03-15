# Task: Cross-Channel Sync Plan

Generate a sync plan from channel configurations and sync rules, ensuring no circular syncs.

## Requirements

1. Read `workspace/channels.json` — an array of channel objects with `id`, `name`, `type` (e.g., `slack`, `email`, `teams`, `discord`), and `content_types` (array of strings like `["messages", "files", "announcements"]`).
2. Read `workspace/sync_rules.json` — an array of rule objects with `source_channel`, `target_channel`, `content_types` (what to sync), and `direction` (`one-way` or `two-way`).
3. Generate `workspace/sync_plan.json` with:
   - `sync_pairs`: array of objects, each with `source`, `target`, `content_types`, and `direction`. For `two-way` rules, create two entries (one for each direction, both with direction `one-way`).
   - `warnings`: array of strings listing any issues found:
     - Content types in a rule that are not supported by the source or target channel.
     - Circular sync paths (A->B->C->A) — detect and warn about these.
   - `channel_summary`: object mapping each channel id to an object with `syncs_to` (array of channel ids) and `syncs_from` (array of channel ids).
4. Only include valid content types (supported by both source and target) in sync_pairs.

## Output

Save the sync plan to `workspace/sync_plan.json`.

# Task: Contact List Management

You are given two contact list files at `workspace/contacts_a.json` and `workspace/contacts_b.json`. Merge them into a single deduplicated list.

## Requirements

1. Read both contact files. Each contains a JSON array of objects with `name`, `email`, `phone`, and `department` fields.
2. Merge the two lists, deduplicating by `email` (case-insensitive). When duplicates are found, keep the entry from `contacts_b.json` (it is considered more recent).
3. Sort the final list alphabetically by `email`.
4. Write the result to `workspace/merged_contacts.json` as a JSON array.

## Output

Save the merged, deduplicated contact list to `workspace/merged_contacts.json`.

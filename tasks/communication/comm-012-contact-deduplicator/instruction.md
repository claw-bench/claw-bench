# Task: Contact Deduplicator

You are given a CSV file at `workspace/contacts.csv` containing contact entries with duplicates. Produce a deduplicated version.

## Requirements

1. Read `workspace/contacts.csv` which has columns: `name`, `email`, `phone`.
2. Identify duplicate contacts by **email address** (case-insensitive comparison).
3. When duplicates are found:
   - Keep the **first occurrence's** name but convert it to **title case** (e.g., "john doe" becomes "John Doe").
   - Keep the **first occurrence's** email in **lowercase**.
   - Keep the **first occurrence's** phone number, normalized to the format `(XXX) XXX-XXXX` (strip any other formatting).
4. Output the deduplicated contacts sorted alphabetically by name.
5. Include the header row in the output.

## Output

Save the deduplicated contacts to `workspace/deduplicated_contacts.csv`.

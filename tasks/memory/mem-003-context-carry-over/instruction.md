# Task: Context Carry-Over

Read the file `workspace/config.json` **once**. It contains application configuration with multiple sections. After reading it, you must create three output files from memory of its contents. Do not re-read config.json while creating the output files.

## Output Files

### 1. `workspace/db_connection.txt`
Write a database connection string in the format:
```
postgresql://<username>:<password>@<host>:<port>/<database>
```
using the values from the `database` section of config.json.

### 2. `workspace/feature_report.txt`
List each feature flag from the `features` section, one per line, in the format:
```
<feature_name>: ENABLED
```
or
```
<feature_name>: DISABLED
```
List them in the same order they appear in config.json.

### 3. `workspace/notification_summary.txt`
Write a summary of the `notifications` section with exactly these lines:
```
Email notifications: <on/off>
Email recipient: <email address>
SMS notifications: <on/off>
SMS phone: <phone number>
Slack webhook: <URL or "not configured">
```
If a notification channel is enabled, write "on"; otherwise write "off". If a value is not present in config.json, write "not configured".

## Rules
- Read config.json only once at the beginning
- All output files go in the `workspace/` directory

Create Apple Reminders from user input.

Parse the user's request in $ARGUMENTS to extract reminder title, datetime, and optionally list name (default: "paper work").

Run the script for each reminder:
```
bash ~/Dev/tools/mactools/raycast/commands/create_reminder.sh "<title>" "<YYYY-MM-DD HH:MM>" "<list>"
```

Rules:
- If user gives relative dates like "明天", "下周四", convert to absolute YYYY-MM-DD based on today's date
- If no time specified, default to 09:00
- If user gives a table/image with multiple items, create one reminder per item
- Confirm what was created after done

# ShareToLinkBot

A Telegram bot that turns your uploaded files into one-time download links using [file.io](https://www.file.io).

## Features

- /start — Welcome message with buttons
- /broadcast — Admin can send messages to all users
- /status — Check user count and file upload stats
- file.io upload with auto-expiring links

## Setup

1. Replace `BOT_TOKEN` and `ADMIN_ID` in `bot.py`
2. Run:

```bash
pip install -r requirements.txt
python bot.py
```
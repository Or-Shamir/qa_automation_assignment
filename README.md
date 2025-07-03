
# 📬 Trello–Gmail Sync Automation

This project validates synchronization between Gmail emails and Trello cards using Python.
It checks that emails are properly reflected as Trello cards, 
verifies labels like "Urgent", and ensures merged descriptions work correctly.

The validations are done both by API method and by UI method

---

## 🚀 Features

- Connects to Gmail API and fetches recent messages.
- Connects to Trello API and reads cards and labels.
- Validates:
  - Email subjects exist as card titles.
  - Body content is included in the card description.
  - "Urgent" emails have the "Urgent" Trello label.
  - Multiple emails with the same subject merge into one card description.

---

## 🧰 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```



## 🔐 Credentials Setup

To run this project, you need to create the following credentials files locally:

1. `credentials_Trello.json`
2. `credentials_Gmail.json`

Use the example files to create your own:

```bash
cp credentials_Trello.example.json credentials_Trello.json
cp credentials_Gmail.example.json credentials_Gmail.json
```

Then, fill them in with your actual credentials. These files are excluded from version control using `.gitignore`.

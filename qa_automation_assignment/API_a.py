
import requests
import pickle
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials


SCOPES = ["https://mail.google.com/"]


with open('credentials_Trello.json') as f:
    credentials_T = json.load(f)

TRELLO_KEY = credentials_T['trello_api_key']
TRELLO_TOKEN = credentials_T['trello_api_token']
BOARD_ID = credentials_T['board_id']



def get_gmail_service():
    creds = None
    token_path = 'token.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials/your_google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


# -------- Gmail API Setup -------- #

def load_gmail_credentials():
    creds = None
    token_path = 'token.json'

    # אם כבר יש טוקן שמור - נטען אותו
    if os.path.exists(token_path):
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # אם אין טוקן או שהוא לא בתוקף - נריץ את ה-Flow מחדש
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials/your_google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # נשמור את הטוקן לפעם הבאה
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_gmail_service_API():
    creds = load_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)

    # דוגמה - קבלת רשימת תוויות (labels)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    print('Labels:')
    for label in labels:
        print(label['name'])




def get_emails_with_subject_and_body(service):
    results = service.users().messages().list(userId='me', maxResults=20).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        body = ''
        if 'parts' in msg_data['payload']:
            for part in msg_data['payload']['parts']:
                if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                    import base64
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        emails.append({'subject': subject, 'body': body})
    return emails

# -------- Trello API Setup -------- #


def get_trello_cards():
    url = f'https://api.trello.com/1/boards/{BOARD_ID}/cards'
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=params)
    return response.json()

def get_trello_labels():
    url = f'https://api.trello.com/1/boards/{BOARD_ID}/labels'
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=params)
    return response.json()

# -------- Main Test -------- #
def normalize(text):
    return " ".join(text.strip().lower().split()) if text else ""

def test_trello_gmail_sync():
    error_count = 0

    service = get_gmail_service()
    emails = get_emails_with_subject_and_body(service)
    trello_cards = get_trello_cards()
    trello_labels = get_trello_labels()

    # ---------- בדיקת קיומה של התווית Urgent ----------
    urgent_label_id = next(
        (l['id'] for l in trello_labels if normalize(l['name']) == 'urgent'), None
    )
    assert urgent_label_id, "❌ No 'Urgent' label found on Trello board."

    # ---------- בדיקת התאמת נושאים במיילים מול שמות כרטיסים ב-Trello ----------
    for email in emails:
        subject = normalize(email['subject'])
        matching_cards = [
            c for c in trello_cards if normalize(c['name']) == subject
        ]

        if not matching_cards:
            print(f"❌ Email subject '{email['subject']}' found in Gmail but not in Trello.")
            error_count += 1
        else:
            # אם המייל מוגדר כ-Urgent - נבדוק שהתווית קיימת בכרטיס
            if 'urgent' in normalize(email['body']):
                for card in matching_cards:
                    if urgent_label_id not in card.get('idLabels', []):
                        print(f"❌ Urgent label missing on Trello card: '{card['name']}'")
                        error_count += 1

    # ---------- בדיקת Merge - כל גוף מייל צריך להופיע בתיאור של הכרטיס ----------
    subjects_to_bodies = {}

    for email in emails:
        subject = normalize(email['subject'])
        body = email['body'].strip()
        subjects_to_bodies.setdefault(subject, []).append(body)

    for subject, bodies in subjects_to_bodies.items():
        matching_cards = [
            c for c in trello_cards if normalize(c['name']) == subject
        ]

        if len(matching_cards) != 1:
            print(f"❌ Expected 1 card for subject '{subject}', but found {len(matching_cards)} cards.")
            error_count += 1
            continue

        card = matching_cards[0]
        card_desc = card.get('desc', '').lower()

        for body in bodies:
            if normalize(body) not in card_desc:
                print(f"❌ Email body not found in card description for subject '{subject}': Body snippet: '{body[:30]}...'")
                error_count += 1

    print(f"\n✅ Test finished. Total errors: {error_count}")
    assert error_count == 0, f"Test failed with {error_count} errors!"


import re
import json
import os
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials
import base64
import requests
from googleapiclient.errors import HttpError

SCOPES = ["https://mail.google.com/"]

def test_trello_gmail_sync():
    error_count = 0
    service = get_gmail_service()
    emails = get_emails_with_subject_and_body(service)
    trello_cards = get_trello_cards()
    trello_labels = get_trello_labels()

    if not emails or not trello_cards or not trello_labels:
        print("❌ Aborting test due to failed data fetch.")
        return

    # Validate "Urgent" label presence
    urgent_label_id = next((l['id'] for l in trello_labels if normalize(l['name']) == 'urgent'), None)
    if not urgent_label_id:
        print("❌ No 'Urgent' label found on Trello board.")
        error_count += 1

    subjects_to_bodies = {}

    print("\n\033[1mChecking 'Matched subjects' condition:\033[0m")
    for email in emails:
        subject = normalize(email['subject'])
        subjects_to_bodies.setdefault(subject, []).append(email['body'].strip())

        # Check for card with this subject
        matching_cards = [c for c in trello_cards if subject in normalize(c['name'])]

        if not matching_cards:
            print(f"\n ❌ Email subject '{email['subject']}' found in Gmail but not in Trello.")
            error_count += 1
            continue

        # Urgent label validation
        if 'urgent' in normalize(email['body']):
            for card in matching_cards:
                if urgent_label_id not in card.get('idLabels', []):
                    print(f"❌ Urgent label missing on Trello card: '{card['name']}'")
                    error_count += 1

    # Validate merged descriptions
    print("\n\033[1mChecking 'Merged' condition:\033[0m")
    for subject, bodies in subjects_to_bodies.items():
        matching_cards = [c for c in trello_cards if normalize(c['name']) == subject]

        if len(matching_cards) != 1:
            print(f"\n ❌ Expected 1 card for subject '{subject}', but found {len(matching_cards)} cards.")
            error_count += 1
            continue

        card = matching_cards[0]
        card_desc = normalize(card.get('desc', ''))

        for body in bodies:
            if normalize(body) not in card_desc:
                print(f"❌ Email body not found in card description for '{subject}': '{body[:30]}...'")
                error_count += 1

    print(f"\n✅ Sync Check Completed. Total errors: {error_count}")
    assert error_count == 0, f"Test failed with {error_count} errors!"



with open('credentials_Trello.json') as f:
    credentials_T = json.load(f)

TRELLO_KEY = credentials_T['trello_api_key']
TRELLO_TOKEN = credentials_T['trello_api_token']
BOARD_ID = credentials_T['board_id']

def get_trello_cards():
    """ Extract all the current Trello cards"""
    try:
        url = f'https://api.trello.com/1/boards/{BOARD_ID}/cards'
        params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch Trello cards: {e}")
        return []


def get_trello_labels():
    """ Extract all the current Trello labels"""
    try:
        url = f'https://api.trello.com/1/boards/{BOARD_ID}/labels'
        params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch Trello labels: {e}")
        return []


def get_gmail_service():
    """ Connects to gmail API"""
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


def get_emails_with_subject_and_body(service, max_results=50):
    """ Extract all the current Emails with amount limitation"""
    emails = []
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
    except HttpError as e:
        print(f"❌ Failed to fetch email list: {e}")
        return emails

    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')

            body = ''
            payload = msg_data.get('payload', {})
            parts = payload.get('parts', [])

            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        try:
                            decoded_body = base64.urlsafe_b64decode(data).decode('utf-8')
                            body += decoded_body
                        except Exception as e:
                            print(f"⚠️ Failed to decode body: {e}")
            emails.append({'subject': subject, 'body': body})

        except HttpError as e:
            print(f"❌ Failed to fetch email content: {e}")
    return emails


def normalize(text):
    """ Attempt to remove spaces and manipulate the text, so the chance of a match will increase"""
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)  # collapse whitespace
    return text




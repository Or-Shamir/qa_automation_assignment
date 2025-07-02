import pytest
from typing import List, Dict
from qa_automation_assignment.page_objects.gmail_page import GmailPage
from qa_automation_assignment.page_objects.trello_page import TrelloBoardPage
from qa_automation_assignment.utils.utils import trello_credentials
import json
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from qa_automation_assignment.page_objects.trello_page import TrelloBoardPage

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]

@pytest.fixture
def example_of_injected_item():
    return {'a': 1}


def test_gmail_login(example_of_injected_item: dict[str, int]):
    gmail = GmailPage(page)
    creds = GmailPage.gmail_login()

    assert len(creds.client_id) > 0
    # assert creds.token_uri == "https://oauth2.googleapis.com/token"

    assert example_of_injected_item.get('b', None) is None
    assert example_of_injected_item.get('a', None) == 1

def test_main_func(page):
  f = trello_credentials()
  trello = TrelloBoardPage(page)
  trello.trello_login(f['trello_email'], f['trello_pass'])
  u_cards = trello.get_all_cards_with_urgent_label()
  print(u_cards)

  # creds: Credentials = gmail_login()
  # return print_labels(creds)


def test_find_urgent_and_extract():
    """
    1. Login to trello
    2. Find all cards with 'Urgent' label across all columns
    3. For each urgent card, extract:
    - Card title
    - Card description
    - Labels
    - Current status (To Do, In Progress, Done)
    """


def test_simple(example_of_injected_item):

    example_of_injected_item['b'] = 10
    example_of_injected_item['a'] += 1

    assert example_of_injected_item['a'] == 2


def exception_raising_func():
    raise ValueError("Exception 123 raised")


def test_match():
    with pytest.raises(ValueError, match=r".* 123 .*"):
        exception_raising_func()

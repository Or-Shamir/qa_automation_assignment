import pytest
from playwright.sync_api import sync_playwright
import os
import json

def trello_credentials():
    # Load from credentials.json instead of env vars
    with open('../credentials_Trello.json', 'r') as f:
        credentials = json.load(f)
    return credentials
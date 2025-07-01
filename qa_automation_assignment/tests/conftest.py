
import pytest
from playwright.sync_api import sync_playwright
import os
import json

@pytest.fixture(scope="session")
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(playwright_browser):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        yield page
        browser.close()

@pytest.fixture(scope="session")
def trello_credentials():
    # Load from credentials.json instead of env vars
    with open('../credentials.json', 'r') as f:
        credentials = json.load(f)
    return credentials
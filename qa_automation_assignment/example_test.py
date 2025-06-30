import pytest
import json
from main import gmail_login


@pytest.fixture
def example_of_injected_item():
    return {'a': 1}


def test_gmail_login(example_of_injected_item: dict[str, int]):
    creds = gmail_login()

    assert len(creds.client_id) > 0
    # assert creds.token_uri == "https://oauth2.googleapis.com/token"

    assert example_of_injected_item.get('b', None) is None
    assert example_of_injected_item.get('a', None) == 1



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

def test_start_session():
    import pytest
    from playwright.sync_api import sync_playwright
    import os

    @pytest.fixture(scope="session")
    def playwright_browser():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            yield browser
            browser.close()

    @pytest.fixture(scope="function")
    def page(playwright_browser):
        context = playwright_browser.new_context()
        page = context.new_page()
        yield page
        context.close()

    @pytest.fixture(scope="session")
    def trello_credentials():
        return {
            "email": os.getenv("TRELLO_EMAIL"),
            "password": os.getenv("TRELLO_PASSWORD")
        }


def test_simple(example_of_injected_item):

    example_of_injected_item['b'] = 10
    example_of_injected_item['a'] += 1

    assert example_of_injected_item['a'] == 2


def exception_raising_func():
    raise ValueError("Exception 123 raised")


def test_match():
    with pytest.raises(ValueError, match=r".* 123 .*"):
        exception_raising_func()

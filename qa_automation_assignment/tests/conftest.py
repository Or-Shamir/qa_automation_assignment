
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000,
            args=['--start-maximized']
        )
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(playwright_browser):
        page = playwright_browser.new_page()
        yield page
        page.close()


from playwright.sync_api import Page, Locator, expect
import json

class TrelloBoardPage:
    def __init__(self, page: Page):
        self.page = page


    def trello_login(self,trello_email: str, trello_pass: str):
        self.page.goto("https://trello.com/b/2GzdgPlw/droxi")

        # If already logged in and redirected to board or homepage, skip
        if 'https://trello.com/b/2GzdgPlw/droxi' in self.page.url and '/login' not in self.page.url:
            print("Already logged in (session preserved). Skipping login.")
            return

        try:
            # Check if email input is visible
            if self.page.is_visible('a[href*="/login"]'):
                self.page.click('a[href*="/login"]')
                print("Filling credentials...")
                self.page.fill('input[data-testid="username"]', trello_email)
                self.page.click('button#login-submit')  # Go to blue 'continue' btn

                self.page.fill('input[data-testid="password"]', trello_pass)
                self.page.click('button#login-submit')
            return

        except Exception as e:
            print(f"Login skipped or elements not found (possibly already logged in): {e}")

        # Final check: confirm successful login
        assert "login" not in self.page.url, "Login failed or still on login page."


    def get_urgent_cards(self):
        urgent_cards = []
        columns = self.page.query_selector_all('.list')  # Trello columns (lists)
        for column in columns:
            column_title = column.query_selector('.list-header-name-assist').inner_text()
            cards = column.query_selector_all('.list-card')
            for card in cards:
                labels = [label.inner_text() for label in card.query_selector_all('.card-label')]
                if any('Urgent' in label for label in labels):
                    card_title = card.query_selector('.list-card-title').inner_text()
                    card_description = self.extract_card_description(card)
                    urgent_cards.append({
                        'Title': card_title,
                        'Description': card_description,
                        'Labels': labels,
                        'Status': column_title
                    })
        return urgent_cards
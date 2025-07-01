from playwright.sync_api import Page, Locator, expect
import json
from typing import List, Dict


class TrelloBoardPage:
    def __init__(self, page: Page):
        self.page = page
        self.filters_btn = self.page.get_by_test_id("filter-popover-button")
        self.select_labels_dropdown = self.page.locator('[role="listbox"]')
        self.filter_x_btn = self.page.get_by_role("button", name="Close popover")
        self.find_n_of_lists_in_board = self.page.get_by_test_id("list-wrapper")
        self.card_title_locator = self.page.get_by_test_id("card-name")
        self.card_labels_locator = self.page.get_by_test_id("card-back-labels-container")
        self.card_description_locator = self.page.get_by_test_id("description-content-area")
        self.card_x_btn = self.page.get_by_test_id("CloseIcon")


    def trello_login(self,trello_email: str, trello_pass: str):
        self.page.goto("https://trello.com/b/2GzdgPlw/droxi")

        # If already logged in and redirected to board or homepage, skip
        if 'https://trello.com/b/2GzdgPlw/droxi' in self.page.url and self.page.locator("h1.vTffz8o0OD6vJR").is_hidden():
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

    def get_all_cards_with_urgent_label(self) -> List[Dict]:
        """Get all cards with 'Urgent' label across all columns"""

        # click on the 'filters' icon
        self.filters_btn.click()

        self.select_label("Urgent")
        self.x_btn.click()
        self.find_n_of_lists_in_board
        card = 0
        while card < self.find_n_of_lists_in_board:

        title = self.open_card()
        #.get_card_title()
        labels = self.get_card_labels()
        description = self.get_card_description()

        self.close_card()

        return {
            "title": title,
            "labels": labels,
            "description": description
        }

    def open_card(self, card_name):
        # פותח את הכרטיס לפי השם שלו
        self.page.locator(f'text="{card_name}"').first.click()

    def get_card_title(self):
        return self.page.locator(self.card_title_locator).inner_text()

    def get_card_labels(self):
        labels = self.page.locator(self.card_labels_locator).all()
        return [label.inner_text() for label in labels]

    def get_card_description(self):
        return self.page.locator(self.card_description_locator).inner_text()

    def close_card(self):
        self.page.locator(self.close_button_locator).click()

    def get_card_details(self, card_name):
        # פותח כרטיס, שואב פרטים, סוגר
        self.open_card(card_name)


    def select_label(self, label_name):
        # פותח את התפריט
        self.page.get_by_placeholder("Select labels").click()

        # לוקח את הרשימה שנפתחה
        dropdown_options = self.page.locator('[role="listbox"]')

        # בודק אם הלייבל קיים
        target_option = dropdown_options.locator(f"text={label_name}")
        if target_option.count() == 0:
            raise Exception(f"Label '{label_name}' not found in dropdown options.")

        # מגלגל אליו אם צריך ולוחץ
        target_option.scroll_into_view_if_needed()
        target_option.click()
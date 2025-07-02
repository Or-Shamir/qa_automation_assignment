from playwright.sync_api import Page, Locator, expect
import json
from typing import List, Dict, Any


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
        self.card_x_btn = self.page.get_by_role("button", name="Close popover")


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

    def get_all_cards_with_urgent_label(self) -> tuple[Locator, list[Any]]:
        """Get all cards with 'Urgent' label across all columns"""

        # click on the 'filters' icon
        self.filters_btn.click()
        self.select_label("Urgent")
        self.card_x_btn.click()
        self.get_cards_per_column()
        data = self.extract_info_from_filtered_cards()
        return  data

#אחרי סינון
    def get_cards_per_column(self):
        columns = self.find_n_of_lists_in_board
        columns_data = {}

        num_of_columns = columns.count()
        print(f"Found {num_of_columns} columns")

        for i in range(num_of_columns):
            column = columns.nth(i)

            # כותרת העמודה
            column_title = column.nth(i).page.get_by_test_id("list-name-textarea").all_text_contents()

            # כרטיסים בעמודה
            visable_cards = column.locator('[data-testid="list-card-wrapper"]:visible')        #.page.get_by_test_id("list-card-wrapper").filter()
            num_of_cards = visable_cards.count()
            print(f"Found {num_of_cards} cards in column '{column_title}'")

            card_titles = []
            for j in range(num_of_cards):
                card_title = visable_cards.nth(j).page.get_by_test_id('card-name').first.inner_text()
                card_titles.append(card_title)
                j += 1

            columns_data[column_title] = card_titles
            i += 1

        return columns_data


#מוציאה מידע מכל כרטיס ושומרת
    def extract_info_from_filtered_cards(self):
        cards = self.page.locator('.list-card')
        all_card_data = []

        for i in range(cards.count()):
            card = cards.nth(i)
            card_title = card.locator(self.card_title_locator).inner_text()

            # לוחצת על הכרטיס
            card.click()

            # שולפת פרטי כרטיס
            title = self.card_title_locator.inner_text()
            labels = [label.inner_text() for label in self.card_labels_locator.all()]
            description = self.card_description_locator.inner_text()

            # שומרת
            all_card_data.append({
                "title": title,
                "labels": labels,
                "description": description
            })

            # סוגרת את הכרטיס
            self.page.get_by_role("button", name="Close popover").click()

        return all_card_data





    def select_label(self, label_name):

        labels_section = self.page.locator('p.pLccPkFlgt7FfH', has_text="Labels")
        labels_section.scroll_into_view_if_needed()
        labels_section.wait_for(state='visible')

        # open the dropdown menu of the labels
        labels_section.locator('xpath=following::input[@role="combobox"]').first.click()

        option = self.page.locator('div[role="option"]', has_text=label_name)

        if option.count() == 0:
            raise Exception(f"Label '{label_name}' not found in dropdown!")

        option.scroll_into_view_if_needed()
        option.click()

        # # פותח את התפריט
        # self.page.get_by_placeholder("Select labels").click()
        #
        # # לוקח את הרשימה שנפתחה
        # dropdown_options = self.page.locator('[role="listbox"]')
        #
        # # בודק אם הלייבל קיים
        # target_option = dropdown_options.locator(f"text={label_name}")
        # if target_option.count() == 0:
        #     raise Exception(f"Label '{label_name}' not found in dropdown options.")
        #
        # # מגלגל אליו אם צריך ולוחץ
        # target_option.scroll_into_view_if_needed()
        # target_option.click()
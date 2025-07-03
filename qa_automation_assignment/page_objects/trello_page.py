from playwright.sync_api import Page, Locator, expect
import re

class TrelloBoardPage:
    def __init__(self, page: Page):
        self.page = page
        self.filters_btn = self.page.get_by_test_id("filter-popover-button")
        self.select_labels_dropdown = self.page.locator('[role="listbox"]')
        self.filter_x_btn = self.page.get_by_role("button", name="Close popover")
        self.find_n_of_lists_in_board = self.page.get_by_test_id("list-wrapper")
        self.card_title_locator = self.page.get_by_test_id("card-name")
        self.card_labels_locator = self.page.get_by_test_id("card-back-labels-container") ##compact-card-label
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


    def get_all_cards_with_urgent_label(self) :
        """Get all cards with 'Urgent' label across all columns"""
        # click on the 'filters' icon
        self.filters_btn.click()
        self.select_label("Urgent")
        self.card_x_btn.click()
        self.get_cards_per_column()
        data = self.extract_info_from_filtered_cards()
        return data


    def get_cards_per_column(self):
        """after filtering only the urgent cards"""
        columns = self.find_n_of_lists_in_board
        columns_data = {}

        num_of_columns = columns.count()
        print(f"Found {num_of_columns} columns")

        for i in range(num_of_columns):
            column = columns.nth(i)

            # Column title-takes the first one
            column_title_list = column.get_by_test_id("list-name-textarea").all_text_contents()
            column_title = column_title_list[0]

            # count how many cards in a column
            visible_cards = column.locator('[data-testid="list-card-wrapper"]:visible')
            num_of_cards = visible_cards.count()
            print(f"Found {num_of_cards} cards in column '{column_title}'")

            card_titles = []
            for j in range(num_of_cards):
                card_title = visible_cards.nth(j).page.get_by_test_id('card-name').first.inner_text()
                card_titles.append(card_title)

            columns_data[column_title] = card_titles
        return columns_data


    def extract_info_from_filtered_cards(self):
        """Extract card data and save"""
        cards = self.page.locator('[data-testid="list-card-wrapper"]:visible')
        all_card_data = []

        for i in range(cards.count()):
            card = cards.nth(i)
            card_title = card.locator(self.card_title_locator).inner_text()

            # Open the card to extract details
            card.click()
            title = card_title
            labels = [label.inner_text() for label in self.card_labels_locator.all()]
            status = self.page.locator("span.wl2C35O7dKV1wx").inner_text()
            try:
                description = self.page.get_by_test_id("description-content-area").inner_text()
            except Exception as e:
                print(f"⚠️ Description not found for card '{title}': {e}")
                description = ""

            card_data = {
                "title": title,
                "labels": labels,
                "status": status,
                "description": description
            }
            all_card_data.append(card_data)

            # Close card modal
            self.page.get_by_role("button", name="Close dialog").click()

            # ✅ Print card info nicely
            print("\n📌 Card Details:")
            print(f"🔹 Title      : {title}")
            cleaned_labels = [label.strip().replace('\n', ' , ') for label in labels]
            print(f"🔸 Labels     : {' , '.join(cleaned_labels) if cleaned_labels else 'No labels'}")
            print(f"🔹 Status     : {status}")
            print(f"🔸 Description: {description if description else 'No description'}")

        print(f"\n✅ Total cards processed: {len(all_card_data)}")
        # return all_card_data

    def select_label(self, label_name):
        """scroll down inside the filter dialog, find the Labels section and choose 'Urgent' in dropdown"""
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

    def test_validate_specific_card_details(self):
        """find specific card and extract data to validate expected values"""
        errors = []
        card_title = "summarize the meeting"
        try:
            card = self.page.get_by_test_id("card-name").filter(has_text=card_title).first
            card.click()
        except Exception as e:
            errors.append(f"❌ Failed to open card '{card_title}': {e}")
            # If failed to open the card, no point to continue
            print("\n".join(errors))
            return

        # Validate Title
        try:
            header_title = self.page.get_by_test_id("card-back-title-input").input_value()
            if header_title.strip() != card_title:
                errors.append(f"❌ Title mismatch: got '{header_title.strip()}', expected '{card_title}'")
        except Exception as e:
            errors.append(f"❌ Failed to read title: {e}")

        # Validate Description
        try:
            description = self.page.get_by_test_id("description-content-area").inner_text()
            clean_description = re.sub(r'\s+', ' ', description.strip())
            expected = "For all of us Please do so"

            if clean_description != expected:
                errors.append(
                    f"❌ Description mismatch: got '{description.strip()}', expected '{expected}' (after normalization)")
        except Exception as e:
            errors.append(f"❌ Failed to read description: {e}")

        # Validate Labels
        try:
            labels = [label.inner_text() for label in self.card_labels_locator.all()]
            if not any("New" in label for label in labels):
                errors.append(f"❌ 'New' label not found. Found labels: {labels}")
        except Exception as e:
            errors.append(f"❌ Failed to read labels: {e}")

        # Validate status (column name inside modal)
        try:
            status = self.page.locator("span.wl2C35O7dKV1wx").inner_text().strip()
            if status != "To Do":
                errors.append(f"❌ Status mismatch: found '{status}' (expected 'To Do')")
        except Exception as e:
            errors.append(f"❌ Failed to read status: {e}")

        # Closing the dialog
        self.page.get_by_role("button", name="Close dialog").click()


        # Summary
        if errors:
            print("\n".join(errors))
            assert False, "❌ Some validations failed"
        else:
            print("✅ All validations passed for 'summarize the meeting' card.")
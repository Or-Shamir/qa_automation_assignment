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



def gmail_login():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  return creds

#API

def print_labels(creds):
    try:
      # Call the Gmail API
      service = build("gmail", "v1", credentials=creds)
      results = service.users().labels().list(userId="me").execute()

      labels = results.get("labels", [])

      if not labels:
        print("No labels found.")
        return
      print("Labels:")
      for label in labels:
        print(label["name"])

    except HttpError as error:
      # TODO(developer) - Handle errors from gmail API.
      print(f"An error occurred: {error}")


def load_credentials():
  with open('credentials.json') as f:
    return json.load(f)


def main(page):
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  f = load_credentials()
  trello = TrelloBoardPage(page)
  trello.trello_login(f['trello_email'], f['trello_pass'])

  creds: Credentials = gmail_login()
  return print_labels(creds)


if __name__ == "__main__":
  main()



  def get_all_cards_with_urgent_label(self) -> List[Dict]:
        """Get all cards with 'Urgent' label across all columns"""

        # Claud func

        # urgent_cards = []
        #
        # # Get all lists (columns)
        # lists = self.page.locator(self.list_selector).all()
        #
        # for list_element in lists:
        #     # Get column name
        #     column_name = list_element.locator("[data-testid='list-name']").text_content().strip()
        #
        #     # Get all cards in this column
        #     cards = list_element.locator(self.card_selector).all()
        #
        #     for card in cards:
        #         # Check if card has urgent label (red label)
        #         urgent_labels = card.locator(self.urgent_label_selector).all()
        #
        #         if urgent_labels:
        #             card_title = card.text_content().strip()
        #
        #             # Click on card to get more details
        #             card.click()
        #             self.wait_for_element(self.card_modal_selector)
        #
        #             # Extract card details from modal
        #             description = self._get_card_description()
        #             labels = self._get_card_labels()
        #
        #             urgent_cards.append({
        #                 'title': card_title,
        #                 'description': description,
        #                 'labels': labels,
        #                 'status': column_name
        #             })
        #
        #             # Close modal
        #             self._close_card_modal()

        # return urgent_cards
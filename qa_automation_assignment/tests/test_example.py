
from qa_automation_assignment.utils.utils import trello_credentials
from qa_automation_assignment.page_objects.trello_page import TrelloBoardPage

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]


""" UI section"""

def test_scenario_1(page):
  f = trello_credentials()
  trello = TrelloBoardPage(page)
  trello.trello_login(f['trello_email'], f['trello_pass'])
  u_cards = trello.get_all_cards_with_urgent_label()


def test_scenario_2(page):
  f = trello_credentials()
  trello = TrelloBoardPage(page)
  trello.trello_login(f['trello_email'], f['trello_pass'])
  trello.test_validate_specific_card_details()



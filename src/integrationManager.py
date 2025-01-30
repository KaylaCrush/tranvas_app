from canvasIntegration import CanvasIntegration
from trelloIntegration import TrelloIntegration
from datetime import datetime, timezone

class IntegrationManager:
    def __init__(self, trello = None, canvas = None):
        self.trello = trello if trello else TrelloIntegration()
        self.canvas = canvas if canvas else CanvasIntegration()

    def due_in_days(self, assignment):
        timestamp_dt = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        difference = timestamp_dt-current_time
        return difference.days

    def place_assignment(self, assignment):
        # 0 = unavailable
        # 1 = available
        # 2 = due soon
        # 3 = doing
        # 4 = waiting for grade
        # 5 = graded
        if assignment['submissions']['graded_at'] != None:
            return 4
        if assignment['submissions']['submitted_at'] != None:
            return 3
        if self.due_in_days(assignment) < 12:
            return 1
        return 0

    def create_or_update_assignment(self, assignment):
        if not self.has_assignment_card(assignment):
            return self.create_assignment_card(assignment)
        if self.get_list_index_for_assignment(assignment) != self.place_assignment(assignment):
            return self.move_assignment_card(assignment)
        return {"hey":"LOOKS GOOD BOSS"}


    def create_or_update_all_assignments(self):
        for assignment in self.canvas.all_assignments:
            self.create_or_update_assignment(assignment)
        return "WHAT WHAT"

    def get_list_index_for_assignment(self, assignment):
        for card in self.trello.cards:
            if card['name'] == assignment['name']:
                return self.trello.get_list_index_by_id(card['idList'])
        return -1

    def get_card_for_assignment(self, assignment):
        for card in self.trello.cards:
            if card['name'] == assignment['name']:
                return card
        return "WHOOPS"

    def move_assignment_card(self, assignment, destination_index = None):
        if destination_index == None:
            destination_index = self.place_assignment(assignment)
        card = self.get_card_for_assignment(assignment)
        destination_id = self.trello.get_list_id_by_index(destination_index)

        return self.trello.request_move_card(card['id'],destination_id)


    def create_assignment_card(self,assignment):
        self.trello.cards.append(self.trello.create_card(self.place_assignment(assignment),assignment['name'],assignment['html_url'],assignment['due_at']))

    def has_assignment_card(self,assignment):
        return assignment['name'] in [card['name'] for card in self.trello.cards]

from src.integrations.canvasIntegration import CanvasIntegration
from src.integrations.trelloIntegration import TrelloIntegration
from datetime import datetime, timezone

class IntegrationManager:
    def __init__(self):
        self.trello = TrelloIntegration()
        self.trello.boards=self.trello.get_my_boards()
        self.trello.id = self.trello.find_managed_board()
        self.trello.lists = self.trello.get_lists()
        self.trello.cards = self.trello.get_cards()
        self.trello.labels = self.trello.get_labels()

        self.canvas = CanvasIntegration()
        self.canvas.all_courses = self.canvas.get_all_courses()
        self.canvas.termID = self.canvas.get_current_term_id()
        self.canvas.current_courses = self.canvas.request_current_courses()
        self.canvas.all_assignments = self.canvas.request_assignments()
        self.canvas.course_dict = {course['id']:course['name'].split(" - ")[-1] for course in self.canvas.current_courses}



    def due_in_days(self, assignment):
        timestamp_dt = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        difference = timestamp_dt-current_time
        return difference.days

    def place_assignment(self, assignment):
        # 0 = available
        # 1 = due soon
        # 2 = doing
        # 3 = waiting for grade
        # 4 = graded
        if 'due_at' not in assignment.keys() or assignment['due_at'] == None:
            return 0
        if assignment['submissions']['graded_at'] != None:
            return 4
        if assignment['submissions']['submitted_at'] != None:
            return 3
        if self.due_in_days(assignment) <= 14:
            return 1
        return 0

    def generate_assignment_description(self,assignment):
        return self.canvas.course_dict[assignment['course_id']] + "\n" +assignment['html_url']

    def create_or_update_assignment(self, assignment):
        if not self.has_assignment_card(assignment):
            return self.create_assignment_card(assignment)
        if self.get_list_index_for_assignment(assignment) < self.place_assignment(assignment):
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
        return self.trello.put_card(card['id'],destination_id)

    def get_assignment_label(self, assignment):
        course_name = self.canvas.course_dict[assignment['course_id']]
        label_id = [label['id'] for label in self.trello.labels if label['name'] == course_name][0]
        return label_id

    def create_assignment_card(self,assignment):
        self.trello.cards.append(self.trello.post_card(
            listIndex=self.place_assignment(assignment),
            name=assignment['name'],
            desc=self.generate_assignment_description(assignment),
            due=assignment['due_at'],
            label=self.get_assignment_label(assignment),
            urlSource=assignment['html_url']))

    def has_assignment_card(self,assignment):
        return assignment['name'] in [card['name'] for card in self.trello.cards]

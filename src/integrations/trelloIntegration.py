import os
from requests import get, post, put, delete
from src.integrations.stateManager import StateManager

# API credentials
api_key = os.getenv("TRELLO_KEY")
api_token = os.getenv("TRELLO_TOKEN")

class TrelloIntegration:
    def __init__(self):
        self.sm = StateManager()
        self.id = self.sm.getOrPut('trello_id', self.get_board_id_by_name())
        self.lists = self.sm.getOrPut('trello_lists', self.request_lists())
        self.cards = self.sm.getOrPut('trello_cards', self.request_cards())
        self.labels = self.sm.getOrPut('trello_labels', self.request_get_labels())

    def request(self, url, params={}, request_type=get):
        params.update({
            "key": api_key,
            "token": api_token
        })

        response = request_type(url=url, params=params)

        # Print response
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")

    # #
    # Boards
    # #
    def request_my_boards(self):
        url = "https://api.trello.com/1/members/me/boards"
        return self.request(url)

    def request_create_board(self, name):
        url = "https://api.trello.com/1/boards/"
        params = {'name':name}
        return self.request(url, params=params, request_type=post)

    def request_lists(self):
        url = f"https://api.trello.com/1/boards/{self.id}/lists"
        response = self.request(url)
        return [d['id'] for d in response]

    def get_board_id_by_name(self, board_name = "The CrushBoard"):
        for board in self.request_my_boards():
            if board['name'] == board_name:
                return board['id']


    # #
    # Labels
    # #
    def request_get_labels(self):
        url = f"https://api.trello.com/1/boards/{self.id}/labels"
        response = self.request(url)
        return [label for label in response if label['name']!= ""]

    def request_create_label(self, label_name, color, board_id):
        url = "https://api.trello.com/1/labels"
        params = {
            'name':label_name,
            'color':color,
            'idBoard':board_id
        }
        response = self.request(url, params=params, request_type=post)
        return response


    # #
    # Lists
    # #
    def get_list_index_by_id(self,listID):
        return self.lists.index(listID)

    def get_list_id_by_index(self, index):
        return self.lists[index]


    # #
    # Cards
    # #
    def request_cards(self):
        cards = []
        for listID in self.lists:
            url = f"https://api.trello.com/1/lists/{listID}/cards"
            cards += self.request(url)
        return cards

    def request_create_card(self, listIndex, name, desc, due, label):
        url = "https://api.trello.com/1/cards"
        params = {
            "key": api_key,
            "token": api_token,
            "idList":self.lists[listIndex],
            "name":name,
            "desc":desc,
            "due":due,
            "idLabels":[label]
        }
        response = self.request(url, params, request_type=post)
        return response

    def delete_all_cards(self):
        for card in self.cards:
            self.request_delete_card(card['id'])

    def request_delete_card(self, cardID):
        url = f"https://api.trello.com/1/cards/{cardID}"
        return self.request(url,request_type=delete)

    def request_move_card(self, card_id, destination_list_id):
        url = f"https://api.trello.com/1/cards/{card_id}"
        params = {"idList":destination_list_id}
        response = self.request(url, params=params, request_type=put)
        return response



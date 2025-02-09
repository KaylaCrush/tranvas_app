import requests, os
from src.util import make_request

# API credentials
api_key = os.getenv("TRELLO_KEY")
api_token = os.getenv("TRELLO_TOKEN")

class TrelloIntegration:
    def post_card(self, listIndex, name, desc, due, label, urlSource=None):
        url = "https://api.trello.com/1/cards"
        params = {
            "idList":self.list_dict[listIndex],
            "name":name,
            "desc":desc,
            "due":due,
            "idLabels":[label,'Managed By App'],
            "urlSource":urlSource
        }
        response = self.trello_request(url, params, request_type=requests.post)
        return response

    def delete_board(self, board_id):
        url = f"https://api.trello.com/1/boards/{board_id}"
        return self.trello_request(url, request_type=requests.delete)

    def post_board(self, name, params = {}):
        url = "https://api.trello.com/1/boards"
        params.update({'name':name})
        return self.trello_request(url, params, request_type=requests.post)

    def post_list(self, name, idBoard):
        url = f"https://api.trello.com/1/boards/{idBoard}/lists"
        params = {'name':name}
        return self.trello_request(url, params, request_type=requests.post)

    def post_label(self,name,color,idBoard=None):
        url = "https://api.trello.com/1/labels"
        idBoard = idBoard if idBoard else self.id
        query = {
            'name': name,
            'color': color,
            'idBoard': idBoard,
        }
        response = self.trello_request(url,query, request_type=requests.post)
        return response

    def delete_all_cards(self):
        for card in self.cards:
            self.delete_card(card['id'])

    def delete_card(self, cardID):
        url = f"https://api.trello.com/1/cards/{cardID}"
        return self.trello_request(url,request_type=requests.delete)

    def get_cards(self):
        url = f"https://api.trello.com/1/boards/{self.id}/cards"
        return self.trello_request(url)

    def get_list_index_by_id(self,listID):
        return [list['id'] for list in self.lists].index(listID)

    def create_app_board(self,boardName="Canvas App"):
        params = {
            'defaultLabels':'false',
            'defaultLists':'false',
            'idBoardSource':'679aabbe7f95308962f44da9',
            'keepFromSource':'none'
        }
        return self.post_board(boardName,params=params)

    def find_managed_board(self):
        for board in self.boards:
            if 'Managed By App' in board['labelNames'].values():
                return board['id']
        board = self.create_app_board()
        return board[0]['id']

    def get_my_boards(self):
        url = "https://api.trello.com/1/members/me/boards"
        return self.trello_request(url)

    def trello_request(self, url, params={}, request_type=requests.get):
        params.update({
            "key": api_key,
            "token": api_token
        })
        return make_request(url=url, params=params, request_type=request_type)

    def get_lists(self):
        url = f"https://api.trello.com/1/boards/{self.id}/lists"
        response = self.trello_request(url)
        return response

    def put_card(self, card_id, destination_list_id):
        url = f"https://api.trello.com/1/cards/{card_id}"
        params = {"idList":destination_list_id}
        response = self.trello_request(url, params=params, request_type=requests.put)
        return response

    def get_labels(self):
        url = f"https://api.trello.com/1/boards/{self.id}/labels"
        response = self.trello_request(url)
        return [label for label in response if label['name']!= ""]



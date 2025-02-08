import requests, os

# API credentials
api_key = os.getenv("TRELLO_KEY")
api_token = os.getenv("TRELLO_TOKEN")

class TrelloIntegration:
    def __init__(self):
        self.id = self.request_id()
        self.lists = self.request_lists()
        self.cards = self.request_cards()
        self.labels = self.request_get_labels()
        pass

    def create_card(self, listIndex, name, desc, due, label):
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
        response = self.request(url, params, request_type="POST")
        return response

    def delete_all_cards(self):
        for card in self.cards:
            self.request_delete_card(card['id'])


    def request_delete_card(self, cardID):
        url = f"https://api.trello.com/1/cards/{cardID}"
        return self.request(url,request_type="DELETE")


    def request_cards(self):
        cards = []
        for listID in self.lists:
            url = f"https://api.trello.com/1/lists/{listID}/cards"
            cards += self.request(url)
        return cards

    def get_list_index_by_id(self,listID):
        return self.lists.index(listID)

    def get_list_id_by_index(self, index):
        return self.lists[index]

    def request_id(self):
        url = "https://api.trello.com/1/members/me/boards"
        for board in self.request(url):
            if board['name'] == "The CrushBoard": # TODO: Make this a variable somehow. Environment variable, or something. Maybe find it automatically somehow.
                return board['id']

    def request(self, url, params={}, request_type="GET"):
        params.update({
            "key": api_key,
            "token": api_token
        })

        response = "DERP"
        # Send the request
        if request_type == "GET":
            response = requests.get(url=url, params=params)
        if request_type == "POST":
            response = requests.post(url=url, params=params)
        if request_type == "PUT":
            response = requests.put(url=url, params=params)
        if request_type == "DELETE":
            response = requests.delete(url=url, params=params)

        # Print response
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")

    def request_lists(self):
        url = f"https://api.trello.com/1/boards/{self.id}/lists"
        response = self.request(url)
        return [d['id'] for d in response]

    def request_move_card(self, card_id, destination_list_id):
        url = f"https://api.trello.com/1/cards/{card_id}"
        params = {"idList":destination_list_id}
        response = self.request(url, params=params, request_type="PUT")
        return response

    def request_get_labels(self):
        url = f"https://api.trello.com/1/boards/{self.id}/labels"
        response = self.request(url)
        return [label for label in response if label['name']!= ""]



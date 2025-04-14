from .lobby import Lobby
from .auth import Admin
import requests


class Manager:
    def __init__(self, url, email, password):
        self.url = url
        self.admin = Admin(url, email, password)
        self.lobby = None


    def create_lobby(self, info):
        #TODO: check for how long the token is valid and implement a refresh logic
        #TODO: actually use real infos
        name = info["name"]


        while not self.admin.token:
            self.admin.refresh_token()

        payload = {
            "name": "Serata Romantica Milano",
            "location": {
                "lat": 45.4642,
                "lng": 9.1900
            },
            "matchType": "romantic",
            "eventType": "couple",
            "maxMembers": 2,
            "description": "Una serata romantica nel cuore di Milano",
            "creationDate": "2024-03-20T18:00:00.000Z",
            "preEventDate": "2024-03-20T18:00:00.000Z",
            "eventDate": "2024-03-20T20:00:00.000Z",
            "postEventDate": "2024-03-20T23:00:00.000Z",
            "inviteLink": "https://example.com/invite/milano-romantic",
            "questionSet" : 1
        }


        response = requests.post(self.url+"api/collections/lobbies", json=payload, headers=self.admin.header)
        if response.status_code == 201:
            id = response.json()["id"]
            self.lobby = Lobby(self.url, id)
            self.lobby.get_lobby_info(self.admin.header)
            return True, id
        else:
            return False, -1
            
    def get_lobby_info(self):
        raise NotImplementedError
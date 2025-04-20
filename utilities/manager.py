from .lobby import Lobby
from .admin import Admin
import requests


class Manager:
    def __init__(self, url, email, password):
        self.url = url
        self.admin = Admin(url, email, password)
        self.lobby = None


    def create_lobby(self, payload):
        #TODO: don't create lobby if one exists
        #TODO: actually use real infos


      


        response = requests.post(self.url+"api/collections/lobbies", json=payload)
        if response.status_code == 201:
            id = response.json()["id"]
            self.lobby = Lobby(self.url, id)
            self.lobby.get_lobby_info()
            return True, id
        else:
            return False, -1
            
    def get_lobby_info(self):
        raise NotImplementedError
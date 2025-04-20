import requests
from dateutil import parser
import time



class Lobby:
    def __init__(self, url, id):
        self.id = id
        self.status = None
        self.url = url+"api/collections/lobbies/"
    
    def get_lobby_info(self):
        response = requests.get(self.url+str(self.id))

        
        dt = parser.isoparse(response.json()["creationDate"])
        self.creation_date = dt.timestamp()

        dt = parser.isoparse(response.json()["preEventDate"])
        self.pre_event_date = dt.timestamp()

        dt = parser.isoparse(response.json()["eventDate"])
        self.event_date = dt.timestamp()

        dt = parser.isoparse(response.json()["postEventDate"])
        self.post_event_date = dt.timestamp()
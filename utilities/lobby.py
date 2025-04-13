import requests
from dateutil import parser
import time



class Lobby:
    def __init__(self, url, id, token):
        self.id = id
        self.status = None
        self.url = url+"api/collections/lobbies/"
        self.token = token
        self.header = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer "+self.token
        }
        self.get_lobby_info()
    
    def get_lobby_info(self):
        response = requests.get(self.url+str(self.id), headers=self.header)

        
        dt = parser.isoparse(response.json()["creationDate"])
        self.creation_date = dt.timestamp()

        dt = parser.isoparse(response.json()["preEventDate"])
        self.pre_event_date = dt.timestamp()

        dt = parser.isoparse(response.json()["eventDate"])
        self.event_date = dt.timestamp()

        dt = parser.isoparse(response.json()["postEventDate"])
        self.post_event_date = dt.timestamp()


        print(self.creation_date)
        print(self.pre_event_date)
        print(self.event_date)
        print(self.post_event_date)

    def update_header(self, header):
        self.header = header
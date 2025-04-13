from .lobby import Lobby

import requests

class Admin:
    def __init__(self, url, email, password):
        """
        Instantiate an admin object        
        """
        self.email = email
        self.password = password
        self.url = url
        self.token = None
        self.lobby = None
        if not self.authenticate():
            raise Exception("CANNOT LOGIN")
        self.update_header()
        
    def update_header(self):
        if self.token:
            self.header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer "+self.token
            }

        if self.lobby:
            self.lobby.update_header(self.header)
    
    def authenticate(self):
        if not self.token:
            auth_url = self.url+"api/auth/admins/login"
            payload = {
                "email" : self.email,
                "password" : self.password
            }

            response = requests.post(auth_url, data=payload)
            if response.status_code == 201:
                self.token = response.json()["token"]
                return True
            else:
                print("ERROR MESSAGE: ",response.json()["message"])
                return False
        else:
            return True

    def refresh_token(self):
        auth_url = self.url+"api/auth/admins/login"
        payload = {
            "email" : self.email,
            "password" : self.password
        }

        response = requests.post(auth_url, data=payload)
        if response.status_code == 201:
            self.token = response.json()["token"]
            return True
        else:
            return False
        
    def create_lobby(self):
        #TODO: parametrizza sta roba
        if not self.token:
            self.refresh_token()

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




        response = requests.post(self.url+"api/collections/lobbies", json=payload, headers=self.header)
        if response.status_code == 201:
            id = response.json()["id"]
            self.lobby = Lobby(self.url, id, self.token)
            return True
        else:
            return False

    def get_lobby(self):
        params = {
            "page" : 1,
            "perPage" : 10,
            "order" : "ASC",
            "relations" : "questionSet,questions"
        }

        header = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer "+self.token
        }
        print(self.url+"api/collections/lobbies")
        response = requests.get(self.url+"api/collections/lobbies", headers=header)
        return response




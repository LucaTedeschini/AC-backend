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
        if not self.authenticate():
            raise Exception("CANNOT LOGIN")
        self.update_header()
        
    def update_header(self):
        if self.token:
            self.header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer "+self.token
            }
    def is_token_valid(self):
        #TODO: check for how long the token is valid and implement a refresh logic
        return True
    
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
                self.header = {
                    "Content-Type" : "application/json",
                    "Authorization" : "Bearer "+self.token
                }
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
        



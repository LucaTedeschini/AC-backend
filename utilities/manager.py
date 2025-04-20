from .lobby import Lobby
from .admin import Admin
import requests


class Manager:
    def __init__(self, url, email, password):
        self.url = url
        self.admin = Admin(url, email, password)
        self.lobby = None

    def _make_api_request(self, method, endpoint, **kwargs):
        """
        Helper method to make authenticated API requests
        """
        url = self.url + endpoint
        
        @self.admin.token_required
        def request_with_token(**request_kwargs):
            return method(url, **request_kwargs)
            
        return request_with_token(**kwargs)

    def create_lobby(self, payload):
        #TODO: don't create lobby if one exists

        response = self._make_api_request(
            requests.post,
            "api/collections/lobbies",
            json=payload
        )
        
        if response.status_code == 201:
            self.lobby = Lobby(self.url, response.json())
            return True, self.lobby.id
        else:
            return False, -1
            
    def get_lobby_info(self):
        raise NotImplementedError
from .log import Logger
import requests
from functools import wraps


class Admin:
    def __init__(self, url, email, password):
        """
        Instantiate a Admin object to handle admin authentication and token management.
        """
        self.logger = Logger.get_logger() 
        self.logger.debug("Initializing Admin object with URL: %s, Email: %s", url, email)
        self.email = email
        self.password = password
        self.url = url
        self.token = None
        self.header = None
        if not self.authenticate():
            self.logger.error("Authentication failed for Admin with email: %s", email)
            raise Exception("CANNOT LOGIN")
        self.update_header()

    def update_header(self):
        """
        Update the authorization header with the current token.
        """
        if self.token:
            self.header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token
            }
            self.logger.debug("Header updated with token.")
        else:
            self.logger.warning("Token is not available. Header not updated.")

    def authenticate(self):
        """
        Authenticate the admin and retrieve a token.
        """
        auth_url = self.url + "api/auth/admins/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        self.logger.info("Attempting to authenticate Admin with email: %s", self.email)
        response = requests.post(auth_url, data=payload)
        if response.status_code == 201:
            self.token = response.json()["token"]
            self.update_header()
            self.logger.info("Authentication successful. Token received.")
            return True
        else:
            self.logger.error("Authentication failed. Status code: %d, Message: %s",
                              response.status_code, response.json().get("message", "No message"))
            return False

    def refresh_token(self):
        """
        Refresh the authentication token.
        """
        self.logger.info("Attempting to refresh token for Admin with email: %s", self.email)
        return self.authenticate()

    def before_request(self, func):
        """
        Decorator to add the authorization header to outgoing requests and handle token refresh if needed.
        Retry up to a maximum number of times if the token is invalid.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("BEFORE REQUEST")
        return wrapper
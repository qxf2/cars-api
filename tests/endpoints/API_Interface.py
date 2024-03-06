"""
A composed interface for all the API objects
Use the API_Player to talk to this class
"""

import requests
from .Base_API import Base_API

base_classes = [Base_API]

try:
    from .Cars_Endpoint import CarsEndpoint
    base_classes.append(CarsEndpoint)
except ImportError:
    pass

try:
    from .Register_Endpoint import RegisterEndpoint
    base_classes.append(RegisterEndpoint)
except ImportError:
    pass

try:
    from .Users_Endpoint import UsersEndpoint
    base_classes.append(UsersEndpoint)
except ImportError:
    pass

class API_Interface(*base_classes):
    "A composed interface for the API objects"

    def __init__(self, url, session_flag=False):
        "Constructor"
        # make base_url available to all API endpoints
        self.request_obj = requests
        if session_flag:
            self.create_session()
        self.base_url = url

    def create_session(self):
        "Create a session object"
        self.request_obj = requests.Session()

        return self.request_obj


class UsersEndpoint:

    def users_url(self, suffix=''):
        "Append endpoint to base URI"
        return self.base_url+suffix

 
    def get_users(self, headers):
        """
        Run get request against /users
        
        """
        url = self.users_url(f"/users")
        json_response = self.make_request(method='get', url=url, headers=headers)
        return {
            'url' : url,
            'response' : json_response['json_response']
            }



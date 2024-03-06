
class HomeEndpoint:

    def home_url(self, suffix=''):
        "Append endpoint to base URI"
        return self.base_url+suffix

 
    def get_home(self, headers):
        """
        Run get request against /
        
        """
        url = self.home_url(f"/")
        json_response = self.make_request(method='get', url=url, headers=headers)
        return {
            'url' : url,
            'response' : json_response['json_response']
            }



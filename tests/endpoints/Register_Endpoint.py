
class RegisterEndpoint:

    def register_url(self, suffix=''):
        "Append endpoint to base URI"
        return self.base_url+suffix

 
    def get_register(self, headers):
        """
        Run get request against /register/
        
        """
        url = self.register_url(f"/register/")
        json_response = self.make_request(method='get', url=url, headers=headers)
        return {
            'url' : url,
            'response' : json_response['json_response']
            }


 
    def post_register_car(self, params, headers):
        """
        Run post request against /register/car
        :parameters:
        
        :params: dict
                :name: string
                :brand: string
                :customer_name: string
                :city: string
        """
        url = self.register_url(f"/register/car")
        json_response = self.make_request(method='post', url=url, params=params, headers=headers)
        return {
            'url' : url,
            'response' : json_response['json_response']
            }


 
    def delete_register_car_delete(self, headers):
        """
        Run delete request against /register/car/delete/
        
        """
        url = self.register_url(f"/register/car/delete/")
        json_response = self.make_request(method='delete', url=url, headers=headers)
        return {
            'url' : url,
            'response' : json_response['json_response']
            }



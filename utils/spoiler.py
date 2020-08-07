"""
Adding the decorator to change the return value for the method

"""
import json
import random

def get_random_status():
    "Get the random status"
    status_list = ["301", "500", "502"]
    return random.choice(status_list)


def change_json_value(result):
    "Change the json value"
    result.json.clear()
    result.json['Name']='Null'

    return result


def change_headers(result):
    "Change the headers"
    result.headers._list = [('null','value')]

    return result


class Spoiler():
    "Decorator class to mess with the function returns"
    def vary_me(func):
        "Use this decorator to vary your funtion return value"
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if random.uniform(0,1) < 0.9:
                print("status")
                result.status = get_random_status()
            if random.uniform(0,1) < 0.1:
                print("hi")
                result = change_json_value(result)
            if random.uniform(0,1) < 0.01:
                print("headers")
                result = change_headers(result)

            return result

        return wrapper





    vary_me = staticmethod(vary_me)
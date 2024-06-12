"""
Cars API is a sample web application developed by Qxf2 Services to help testers learn API automation.
This REST application written in Python was built solely to help QA learn to write API automation.
The application has endpoints for you to practice automating GET, POST, PUT and DELETE methods.
It includes endpoints that use URL parameters, jSON payloads, returns different response codes, etc.
We have also included permissioning and authentication too to help you write role based API tests.

IMPORTANT DISCLAIMER: The code here does not reflect Qxf2's coding standards and practices.
"""

import logging
import os
import random
from functools import wraps
import flask
from flask import Flask, session, request, jsonify, abort, render_template
from apitally.flask import ApitallyMiddleware


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.wsgi_app = ApitallyMiddleware(app,
                                  client_id="c945b906-bf5f-4820-9757-1aaf2bae3434",
                                  env="dev")

"""write logs for app
   filehandler of logging  module is not creating log directory if dir does not exist"""
if not os.path.exists('log'):
    os.makedirs('log')
app.logger.addHandler(logging.FileHandler('log/app.log'))
app.logger.setLevel(logging.INFO)

CARS_LIST = [{"name": "Swift", "brand": "Maruti", "price_range": "3-5 lacs", "car_type": "hatchback"},
             {"name": "Creta", "brand": "Hyundai", "price_range": "8-14 lacs", "car_type": "hatchback"},
             {"name": "City", "brand": "Honda", "price_range": "3-6 lacs", "car_type": "sedan"},
             {"name": "Vento", "brand": "Volkswagen", "price_range": "7-10 lacs", "car_type": "sedan"}]

USER_LIST = [{"name": "qxf2", "password": "qxf2", "perm": "admin"},
             {"name": "eric", "password": "testqxf2", "perm": "non_admin"},
             {"name": "morgan", "password": "testqxf2", "perm": "non_admin"},
             {"name": "jack", "password": "qxf2", "perm": "non_admin"}]

registered_cars = []


def check_auth(username, password):
    "check if the given is valid"
    user = [user for user in USER_LIST if user['name']
            == username and user['password'] == password]
    if len(user) == 1:
        return True
    return False


def authenticate_error(auth_flag):
    "set auth message based on the authentication check result"
    if auth_flag is True:
        message = {'message': "Authenticate with proper credentials"}
    else:
        message = {'message': "Require Basic Authentication"}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp


def requires_auth(app_func):
    "verify given user authentication details"
    @wraps(app_func)
    def decorated(*args, **kwargs):
        "Execute app_func only if authentication is valid"
        auth = request.authorization
        auth_flag = True

        if not auth:
            auth_flag = False
            return authenticate_error(auth_flag)
        elif not check_auth(auth.username, auth.password):
            return authenticate_error(auth_flag)
        session['cars_list'] = session.get('cars_list', CARS_LIST.copy())
        return app_func(*args, **kwargs)

    return decorated


def requires_perm():
    "check if the autheticated user has a admin permission"
    auth = request.authorization
    perm_flag = False
    for user in USER_LIST:
        if user['name'] == auth.username and user['perm'] == 'admin':
            perm_flag = True
            return perm_flag
    return perm_flag


@app.route("/", methods=["GET"])
def index_page():
    """this will help test GET without url params"""
    return render_template('index.html')


@app.route("/cars", methods=["GET"])
@requires_auth
def get_cars():
    """this will help test GET without url params"""
    return flask.jsonify({"cars_list": session.get('cars_list'), 'successful': True})


@app.route("/cars/<name>", methods=["GET"])
@requires_auth
def get_car_details(name):
    """this will help test GET with url params"""
    car = [car for car in session.get('cars_list') if car['name'] == name]
    if len(car) == 0:
        resp = jsonify({'message': 'No car found', 'successful': False}), 200
    else:
        resp = jsonify({'car': car[0], 'successful': True}), 200
    return resp


@app.route("/cars/find", methods=["GET"])
@requires_auth
def get_car():
    """this will help test GET with url params"""
    car_name = request.args.get('car_name')
    brand = request.args.get('brand')
    if car_name != "" and car_name is not None and brand != "" and brand is not None:
        car = [car for car in session.get('cars_list') if car['name'] == car_name]
        if len(car) == 0:
            resp = jsonify({'message': 'No car found',
                            'successful': False}), 200
        else:
            resp = jsonify({'car': car[0], 'successful': True}), 200
    else:
        resp = jsonify(
            {'message': 'Not enough url_params', 'successful': False})

    return resp


@app.route("/cars/add", methods=["POST"])
@requires_auth
def add_car():
    """this will help test POST without url params"""
    if not request.json or not 'name' in request.json:
        resp = jsonify({'message': 'Not a json', 'successful': False, }), 400
    car = {
        'name': request.json['name'],
        'brand': request.json['brand'],
        'price_range': request.json['price_range'],
        'car_type': request.json['car_type']
    }
    session.get('cars_list').append(car)
    resp = jsonify({'car': car, 'successful': True}), 200

    return resp


@app.route("/cars/update/<name>", methods=["PUT"])
@requires_auth
def update_car(name):
    """this will help test PUT """
    resp = {}
    car = [car for car in session.get('cars_list') if car['name'] == name]
    if len(car) != 0:
        if not request.json or not 'name' in request.json:
            resp['message'], resp['successful'] = 'Not a json'
            status_code = 404
        else:
            car[0]['name'] = request.json['name']
            car[0]['brand'] = request.json['brand']
            car[0]['price_range'] = request.json['price_range']
            car[0]['car_type'] = request.json['car_type']
            resp['car'], resp['successful'] = car[0], True
            status_code = 200

    else:
        resp['message'], resp['successful'] = 'No car found', False
        status_code = 404

    return jsonify({'response': resp}), status_code


@app.route("/cars/remove/<name>", methods=["DELETE"])
@requires_auth
def remove_car(name):
    """this will help test DELETE"""
    car = [car for car in session['cars_list'] if car['name'] == name]
    if len(car) == 0:
        abort(404)
    session['cars_list'].remove(car[0])

    return jsonify({'car': car[0], 'successful': True}), 200


@app.route('/register/car', methods=['POST'])
@requires_auth
def register_car():
    """this will help test GET and POST with dynamic numbers in url"""
    car_name = request.args.get('car_name')
    brand = request.args.get('brand')
    if car_name != "" and car_name is not None and brand != "" and brand is not None:
        car = [car for car in session.get('cars_list') if car['name'] == car_name]
    customer_details = {
        'customer_name': request.json['customer_name'],
        'city': request.json['city']
    }
    registered_car = {'car': car[0], 'customer_details': customer_details,
                      'registration_token': random.randrange(0, 4), 'successful': True}
    registered_cars.append(registered_car)

    return jsonify({'registered_car': registered_car})


@app.route('/register/', methods=['GET'])
@requires_auth
def get_registered_cars():
    """this will help test GET without url_params"""
    return jsonify({'registered': registered_cars, 'successful': True})


@app.route('/register/car/delete/', methods=['DELETE'])
@requires_auth
def delete_registered_cars():
    """this will help test delete"""
    del registered_cars[0]

    return jsonify({'successful': True}), 200


@app.route('/cars/filter/<car_type>', methods=['GET'])
@requires_auth
def filter_cars(car_type):
    "get cars of the given car type"
    filtered_list = [car for car in session.get('cars_list') if car['car_type'] == car_type]

    return jsonify({'cars': filtered_list})


@app.route('/users', methods=["GET"])
@requires_auth
def get_user_list():
    "return user list if the given authenticated user has admin permission"
    if requires_perm() is True:
        return jsonify({'user_list': USER_LIST, 'successful': True}), 200
    return jsonify({'message': 'You are not permitted to access this resource', 'successful': False}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

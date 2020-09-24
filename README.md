# cars-api

A sample REST application to help testers learn to write API automation.

----
RUN
-----
To run cars api on local machine:- `python cars_app.py`

-------------------------
API ENDPOINTS & EXAMPLES
----------------------------
If you are simply interested in trying out various operations with the requests module, you can can skip the information about creating a session. If you would like to see continuity among your API calls, please create a session.


import requests

my_session = requests.Session()

GET:
1. /cars                    - Get the list of cars
   Example: response = requests.get(url='http://127.0.0.1:5000/cars',auth=(*username,*password))
   Example: response = my_session.get(url='http://127.0.0.1:5000/cars',auth=(*username,*password))

2. /users                   - Get the list of users
   Example: response = requests.get(url='http://127.0.0.1:5000/users',auth=(username,password))
   Example: response = my_session.get(url='http://127.0.0.1:5000/users',auth=(username,password))

3. /cars/filter/<car_type>  - Filter through the list of cars
   Example: response = requests.get(url='http://127.0.0.1:5000/cars/filter/hatchback',auth=(username,password))
   Example: response = my_session.get(url='http://127.0.0.1:5000/cars/filter/hatchback',auth=(username,password))

4. /register                - Get registered cars
   Example: response = requests.get(url='http://127.0.0.1:5000/register',auth=(username,password))
   Example: response = my_session.get(url='http://127.0.0.1:5000/register',auth=(username,password))

5. /cars/< name >             - Get cars by name
   Example: response = requests.get(url='http://127.0.0.1:5000/cars/Swift',auth=(username,password))
   Example: response = my_session.get(url='http://127.0.0.1:5000/cars/Swift',auth=(username,password))

POST:
1. /cars/add                - Add new cars
   Example: response = requests.post(url='http://127.0.0.1:5000/cars/add',json={'name':'figo','brand':'Ford','price_range':'2-3lacs','car_type':'hatchback'},auth=(username,password))
   Example: response = my_session.post(url='http://127.0.0.1:5000/cars/add',json={'name':'figo','brand':'Ford','price_range':'2-3lacs','car_type':'hatchback'},auth=(username,password))

2. /register/car            - Register cars
   Example: response = requests.post(url='http://127.0.0.1:5000/register/car',params={'car_name':'figo','brand':'Ford'},json={'customer_name': 'Unai Emery','city': 'London'},auth=(username,password))
   Example: response = my_session.post(url='http://127.0.0.1:5000/register/car',params={'car_name':'figo','brand':'Ford'},json={'customer_name': 'Unai Emery','city': 'London'},auth=(username,password))

PUT:
1. /cars/update/< name >      - Update car properties
   Example: response = requests.put(url='http://127.0.0.1:5000/cars/update/Vento',json={'name':Vento,'brand':'Ford','price_range':'2-3lacs','car_type':'sedan'},auth=(username,password))
   Example: response = my_session.put(url='http://127.0.0.1:5000/cars/update/Vento',json={'name':Vento,'brand':'Ford','price_range':'2-3lacs','car_type':'sedan'},auth=(username,password))

DELETE:
1. /cars/remove/< name >      - Delete cars from cars_list
   Example: response = requests.delete(url='http://127.0.0.1:5000/register/cars/remove/City',auth=(username,password))
   Example: response = my_session.delete(url='http://127.0.0.1:5000/register/cars/remove/City',auth=(username,password))

2. /car/delete/     - Delete first entry in car registration list
   Example: response = requests.delete(url='http://127.0.0.1:5000/register/car/delete',auth=(username,password))
   Example: response = my_session.delete(url='http://127.0.0.1:5000/register/car/delete',auth=(username,password))

* Get the username & password from user_list in the cars_app.py file 

----
Hosting cars-api in Docker 
-----

The following steps will guide you how to host cars-api in Docker by building an image and launch the application in the Docker container by running the container. 

1. Building the Docker image :

   Run the following command from the terminal 
   
   `docker build --tag cars-api-docker https://github.com/qxf2/cars-api.git#master`

2. Run the Docker container :

   Now run the container for the Docker image. Below is the run command to run the Docker image into the container 
   
   `docker run -d -p 5000:5000 cars-api-docker`

3. Launch the app hosted in Docker container:

   You could launch the URL to verify and proceed the API Testing:
   
    http://localhost:5000
#Dockerfile to build an image/container to host cars-api
#Pull python Image
FROM python
LABEL maintainer = "Qxf2 Services"

#Clone cars-api repository for Docker Image creation
RUN git clone https://github.com/qxf2/cars-api.git

#Set working directory
WORKDIR /cars-api

#Install packages listed in requirements.txt file
RUN pip install -r requirements.txt

#Make port 5000 available to the container
EXPOSE 5000

#Execute command
ENTRYPOINT [ "python" ]
CMD [ "cars_app.py" ]

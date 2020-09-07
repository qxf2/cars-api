#Dockerfile to build an image/container to host cars-api
#Pull python Image
FROM python
LABEL maintainer = "Qxf2 Services"

# Clone files for Docker Image creation
RUN git clone https://github.com/qxf2/cars-api.git

#Set working directory
WORKDIR /cars-api

#Install requirements written in the file
RUN pip install -r requirements.txt

#Port flask app use to the conainer
EXPOSE 5000

#Execute command
ENTRYPOINT [ "python" ]
CMD [ "cars_app.py" ]

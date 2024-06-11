[Unit]
Description=Gunicorn instance to serve carsapi
After=network.target
StartLimitIntervalSec=0

[Service]
WorkingDirectory=${home_directory}/code/cars-api
Environment="PATH=${home_directory}/code/venv-carsapi/bin"
ExecStart=${home_directory}/code/venv-carsapi/bin/gunicorn -b 0.0.0.0:5000 cars_app:app
Restart=always
RestartSec=1

[Install]
WantedBy=multi-user.target

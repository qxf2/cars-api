server {
  listen 80 default_server;
  listen [::]:80 default_server;
  root /var/www/html;
  server_name _;

  location / {
    include proxy_params;
    proxy_pass http://0.0.0.0:5000;
  }
}

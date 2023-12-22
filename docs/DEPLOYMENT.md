Code snippets to help in deployment

sudo -u postgres psql
CREATE DATABASE test_roadflowapi_db1;
CREATE USER test_roadflowapi_user1 WITH PASSWORD 'test';
ALTER ROLE test_roadflowapi_user1 SET client_encoding TO 'utf8';
ALTER ROLE test_roadflowapi_user1 SET default_transaction_isolation TO 'read committed';
ALTER ROLE test_roadflowapi_user1 SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE test_roadflowapi_db1 TO test_roadflowapi_user1;
\q

=======================================

PRODUCTION

======================================

sudo -u postgres psql
CREATE DATABASE roadflow_db;
CREATE USER admin WITH PASSWORD 'test';
ALTER ROLE admin SET client_encoding TO 'utf8';
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE roadflow_db TO admin;

\c roadflow_db
CREATE EXTENSION pg_trgm;

ALTER USER admin CREATEDB;
\q

==============================================

sudo journalctl -u roadflow --since "10 minutes ago" -f

==================================
Setting up roadflow Enviroments
==================================

1. Git clone and setup project

2. Setup gunicorn

    sudo nano /etc/systemd/system/roadflow.socket

[Unit]
Description=Roadflow Gunicorn Socket

[Socket]
ListenStream=/run/roadflow.sock

[Install]
WantedBy=sockets.target


    sudo nano /etc/systemd/system/roadflow.service

[Unit]
Description=Roadflow Gunicorn Service
Requires=roadflow.socket
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/roadflow-api/src
ExecStart=/home/ubuntu/roadflow-api/venv/bin/python \
          /home/ubuntu/roadflow-api/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/roadflow.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target


    sudo systemctl start roadflow.socket
    sudo systemctl enable roadflow.socket

    sudo systemctl start roadflow
    sudo systemctl enable roadflow

    sudo systemctl status roadflow

    sudo systemctl status roadflow.socket

    sudo systemctl daemon-reload

3. Setup Nginx

    sudo nano /etc/nginx/sites-available/roadflow

server {
    listen 80;
    server_name roadflow.tripvalue.com.ng;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/roadflow/src;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/roadflow.sock;
    }
}

ln -s /etc/nginx/sites-available/roadflow /etc/nginx/sites-enabled

sudo nginx -t
sudo systemctl restart nginx
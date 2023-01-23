#!/bin/bash

# Stop service if exists
echo "Stopping BetterYear Service"
systemctl stop better_year

repo_link=$1

# Setup

echo "Setting up git"
cd /opt/
chmod 777 /opt/
apt install -fy git nginx-full python3 python3-pip

# Download App

echo "Removing repo if exists..."
rm -rf /opt/better_year

echo "Cloning into repo..."
git clone $repo_link
cd $repo_link
git pull
pip3 install -r requirements.txt

# Deploy app

echo "Setting up file permissions..."
chown -R root:www-data /opt/better_year
chmod -R 775 /opt/better_year

echo "Copying service to systemd..."
cp server_stuff/better_year.service /etc/systemd/system/

echo "Copying nginx config..."
cp server_stuff/better_year.nginx /etc/nginx/sites-enabled/

echo "Starting nginx..."
nginx -t
systemctl reload nginx

echo "Starting systemd service..."
systemctl daemon-reload
systemctl start better_year
systemctl enable better_year
systemctl status better_year


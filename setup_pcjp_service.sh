#!/bin/bash

# Get the current directory
CURRENT_DIR=$(pwd)
SERVICE_NAME="pcjp"
SERVICE_FILE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
LOG_DIR="${CURRENT_DIR}/log"
ENV_CONF_DIR="/etc/systemd/system/${SERVICE_NAME}.service.d"
ENV_CONF_FILE="${ENV_CONF_DIR}/env.conf"
FLASK_PORT=8080  # You can change this port number as needed

# Ensure the log directory exists
mkdir -p $LOG_DIR

# Ensure the env.conf directory exists
sudo mkdir -p $ENV_CONF_DIR

# Create the service file content
SERVICE_CONTENT="[Unit]
Description=PhenoControl-JP
After=network.target

[Service]
Type=simple
EnvironmentFile=-${ENV_CONF_FILE}
ExecStart=${CURRENT_DIR}/run.sh
ExecStop=${CURRENT_DIR}/stop.sh
Restart=on-failure
RestartSec=5
User=ec2-user
WorkingDirectory=${CURRENT_DIR}
StandardOutput=append:${LOG_DIR}/access.log
StandardError=append:${LOG_DIR}/error.log

[Install]
WantedBy=multi-user.target"

# Create service file
echo "Creating ${SERVICE_FILE_PATH}..."
echo "$SERVICE_CONTENT" | sudo tee $SERVICE_FILE_PATH > /dev/null

# Create the env.conf file content
ENV_CONF_CONTENT="FLASK_PORT=${FLASK_PORT}"

# Create env.conf file
echo "Creating ${ENV_CONF_FILE}..."
echo "$ENV_CONF_CONTENT" | sudo tee $ENV_CONF_FILE > /dev/null

# Reload systemd manager configuration
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling ${SERVICE_NAME} service..."
sudo systemctl enable ${SERVICE_NAME}

# Start the service
echo "Starting ${SERVICE_NAME} service..."
sudo systemctl start ${SERVICE_NAME}

# Check the status of the service
echo "Checking ${SERVICE_NAME} service status..."
sudo systemctl status ${SERVICE_NAME}

echo "${SERVICE_NAME} service setup complete."

#!/bin/bash

# Read username and password from the user
read -p "Enter MySQL DB: " MYSQL_DB
read -p "Enter MySQL username: " MYSQL_USER
read -sp "Enter MySQL password: " MYSQL_PASSWORD
echo

# Docker container service name (as defined in docker-compose.yml)
DOCKER_SERVICE="db"

# Get current timestamp in the format YYYY-MM-DD-HH-mm-ss
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")

# Output filename (with .gz extension for compression)
OUTPUT_FILE="${TIMESTAMP}.sql.gz"

# Perform mysqldump --routines inside the Docker container, pipe to gzip
docker compose exec -T $DOCKER_SERVICE mysqldump --routines -u $MYSQL_USER -p$MYSQL_PASSWORD --all-databases | gzip > $OUTPUT_FILE

# Check if the dump was successful
if [ $? -eq 0 ]; then
    echo "Database dump successfully saved to $OUTPUT_FILE"
else
    echo "Database dump failed"
fi
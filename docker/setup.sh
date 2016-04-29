#!/bin/bash
# On initial setup of the images run this script.

# Create the database first to ensure it is configured correctly before
# Django attempts to connect to it.
docker-compose up -d db
docker-compose up -d web

# Run django migrations
docker-compose exec -d web python manage.py migrate

# Load Postgres with fixture data
docker-compose exec -d web python manage.py loaddata oneanddone_data_dmp.json

docker-compose stop
docker-compose up

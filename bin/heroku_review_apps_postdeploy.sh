#!/bin/bash

python manage.py migrate
python manage.py createsuperuser --noinput --username bsilverberg@mozilla.com --email bsilverberg@mozilla.com
python manage.py createsuperuser --noinput --username rbillings@mozilla.com --email rbillings@mozilla.com

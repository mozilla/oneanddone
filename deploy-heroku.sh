#!/bin/bash

./manage.py collectstatic
./manage.py compress_assets

git add oneanddone/base/static/css/base-min.css
git add oneanddone/base/static/js/base-min.js
git commit -m 'Update base static files'
git push origin master

git push heroku master

heroku run python manage.py migrate

#!/bin/bash

# Checkout master and update
git checkout master
git pull upstream master

python manage.py collectstatic
python manage.py compress_assets

echo "Do you want to deploy to Dev or Prod?"
select env in "Dev" "Prod"; do
    case $env in
        Dev ) s target api.paas.allizom.org; break;;
        Prod ) s target api.paas.mozilla.org; break;;
    esac
done

s login
s group oneanddone
s info

echo "Does everything look ok? Are you ready to continue to push?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "OK, here goes!"; break;;
        No ) exit;;
    esac
done

s update

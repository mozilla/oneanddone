#!/bin/bash

# Name of Stackato executable
if [ -z $STACKATO_EXECUTABLE ]; then
    echo "Set environment variable STACKATO_EXECUTABLE to the name of the Stackato command line executable."
    exit 1
fi

python manage.py collectstatic
python manage.py compress_assets

echo "Do you want to deploy to Dev or Prod?"
select env in "Dev" "Prod"; do
    case $env in
        Dev ) $STACKATO_EXECUTABLE target api.paas.allizom.org; break;;
        Prod ) $STACKATO_EXECUTABLE target api.paas.mozilla.org; break;;
    esac
done

$STACKATO_EXECUTABLE login
$STACKATO_EXECUTABLE group oneanddone
$STACKATO_EXECUTABLE info
$STACKATO_EXECUTABLE env

echo "Does everything look ok? Are you ready to continue to push?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "OK, here goes!"; break;;
        No ) exit;;
    esac
done

$STACKATO_EXECUTABLE push

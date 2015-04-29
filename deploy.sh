#!/bin/bash

# Name of Stackato executable
if [ -z $STACKATO_EXECUTABLE ]; then
    echo "Set environment variable STACKATO_EXECUTABLE to the name of the Stackato command line executable."
    exit 1
fi

python manage.py collectstatic
python manage.py compress_assets

# copy stackato .env file
cp .env .env.saved
cp .env.stackato .env

echo "Do you want to deploy to Dev, Stage or Prod?"
select env in "Dev" "Stage" "Prod"; do
    case $env in
        Dev ) $STACKATO_EXECUTABLE target api.paas.allizom.org; cp stackato-dev.yml stackato.yml; break;;
        Stage ) $STACKATO_EXECUTABLE target api.paas.allizom.org; cp stackato-stage.yml stackato.yml; break;;
        Prod ) $STACKATO_EXECUTABLE target api.paas.mozilla.org; cp stackato-prod.yml stackato.yml; break;;
    esac
done

echo "Do you need to log in?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) $STACKATO_EXECUTABLE login; $STACKATO_EXECUTABLE group oneanddone; break;;
        No ) break;;
    esac
done

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

# copy back .env file
cp .env.saved .env

cp stackato-plain.yml stackato.yml

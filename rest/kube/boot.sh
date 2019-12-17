#!/bin/sh
# this script is used to boot a Docker container
. venv/bin/activate
cd app
#while true ; do read d done	
exec gunicorn -b :5000 --access-logfile - --error-logfile - spot_api:app


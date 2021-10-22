#!/bin/bash

#uwsgi --ini erserver_uwsgi.ini
cd /home/pi/erserver/
/usr/bin/python3 manage.py runserver 0:8888 & /usr/bin/python3 ./auto-timer.py & /usr/bin/python3 ./auto-hint.py &/usr/bin/python3 ./async-player.py


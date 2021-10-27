# from timer.handlers import timer_loop, timer_create
# from mqtt.main import mqtt_routine
# from threading import Thread
import sys
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ers.settings')

application = get_wsgi_application()

# mc_thread = Thread(target=mqtt_routine)
# mc_thread.start()
# timer_create()
# timer_loop()

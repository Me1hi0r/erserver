import os
import django
import time
import logging
import socket
from threading import Timer
import paho.mqtt.client as mqtt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()
from panel.tools import load_current_quest, str_time
from server.settings import MQTT_HOST, MQTT_PORT, TIMER_SUBSCRIBE, TIMER_TOPIC_OUT

# global var
sec = 0
status = ""
timer = None
client = None

def time_init():
    global timer, sec, status

    def timer_loop():
        global sec, status
        if(status == 'START'):
            sec-=1
            client.publish(TIMER_TOPIC_OUT, sec)
            if(sec == 0):
                status = 'STOP'
        if(status == 'STOP' and sec > 0):
            client.publish(TIMER_TOPIC_OUT, sec)

    class CustomTimer(Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    timer = CustomTimer(1, timer_loop)
    quest = load_current_quest()
    sec = quest.playing_time * 60
    status = 'STOP'
    time.sleep(.1)
    timer.start()
    logging.info(f"timer -> initiate {str_time(sec)}")

def mqtt_init(topics):
    global client, sec

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logging.warning("timer/mqtt -> disconnection")

    def on_connect(client, user_data, flags, rc):
        ignore = user_data
        ignore = flags
        for topic in topics:
            client.subscribe(topic)
            logging.info(f"timer/mqtt -> subscribe on {topic}")

    def on_message(client, userdata, message):
        global sec, status
        topic = message.topic
        cmd = message.payload.decode("utf-8")
        if(topic == '/ers/timer/period'):
            sec = int(cmd) * 60
            logging.info(f"timer -> set timer {str_time(sec)}")
        if(topic == '/ers/timer'):
            if cmd == "reset":
                quest = load_current_quest()
                sec = quest.playing_time * 60
                status = 'STOP'
                logging.info(f"timer -> reset {str_time(sec)}")
            if cmd == "start":
                quest = load_current_quest()
                logging.info(f"the timer will start after {quest.start_offset} sec ")
                time.sleep(quest.start_offset)
                sec = quest.playing_time * 60
                status = 'START'
                logging.info(f"timer -> start {str_time(sec)}")
            if cmd == "stop":
                status = 'STOP'
                logging.info(f"timer -> stop")
            if cmd == "add":
                sec += 60
                logging.info(f"timer -> add one minute {str_time(sec)}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

def mqtt_routine(host, port):
    try:
        client.connect(host, port, 6)
        client.loop_start()
        logging.info(f"timer/mqtt -> connect to {host}:{port}")
    except socket.timeout:
        logging.info(f"timer/mqtt -> did'n connect to {host}:{port} -> try again after 30 sec")
        time.sleep(30)
        mqtt_routine(host, port)
    except OSError:
        logging.info(f"timer/mqtt -> network is unreachable -> try again after 30 sec")
        time.sleep(30)
        mqtt_routine(host, port)


mqtt_init(TIMER_SUBSCRIBE)
mqtt_routine(MQTT_HOST, MQTT_PORT)
time_init()


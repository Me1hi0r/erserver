import os
import time
import django
import socket
import logging
import threading
import paho.mqtt.client as mqtt

#neccessary for load data from model
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ers.settings")
django.setup()
from erp.tools import load_ln, quest_riddles
from ers.settings import MQTT_HOST, MQTT_PORT, AUTO_TOPIC_OUT, AUTO_SUBSCRIBE

RID_LIST = []
LN = None
client = None


def publish(name):
    client.publish(AUTO_TOPIC_OUT, name)
    logging.debug(f"timer up, send file {name}")

def auto_hint_init():
    global AUTO_SUBSCRIBE, LN, RID_LIST

    LN = load_ln()
    RID_LIST = []

    #create RIDDLES datastract
    for riddle in quest_riddles():
        topic = f'/er/{riddle.erp_name}/cmd'
        AUTO_SUBSCRIBE.append(topic)
        timers = []
        if riddle.autoi:
            cnt = 0
            for offset in riddle.autoi.split(','):
                timers.append(threading.Timer(int(offset), publish, [f"{riddle.erp_num+cnt}"]))
                cnt += 1
        RID_LIST.append({'num': riddle.erp_num,
                         'topic':topic,
                         'autoi': riddle.autoi,
                         'status': 'none',
                         'timers':timers})
    RID_LIST.sort(key=lambda x: x['num'])
    logging.info(f"auto/hint -> initiate")
    logging.info(f"auto/hint -> create thread timers for all riddle with auto hint")


def mqtt_init(topics):
    global client

    def on_connect(client, user_data, flags, rc):
        ignore = user_data
        ignore = flags
        for topic in topics:
            client.subscribe(topic)
            logging.info(f"auto/hint/mqtt -> subscribe on {topic}")

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logging.warning("auto/hint/mqtt -> disconnection")

    def on_message(client, userdata, message):
        cmd = message.payload.decode("utf-8")
        topic = message.topic
        auto_hint_manage(topic, cmd)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

def auto_hint_manage(topic, cmd):
    global RID_LIST
    if topic == '/erp/auto/hint' and cmd == 'reset':
        logging.info(f"auto/hint -> reset")

        for riddle in RID_LIST:
            for t in riddle['timers']:
                if t.is_alive():
                    t.cancel()
                t.killed = True
        RID_LIST = []
        auto_hint_init()
    if topic == '/er/cmd' and cmd == 'start':
        logging.info(f"auto/hint -> start")
        auto_hint_init()
        if RID_LIST[0]['autoi']:
            for t in RID_LIST[0]['timers']:
                t.start()
                logging.info(f"auto/hint -> start first timer")

    if cmd == 'finish':
        for riddle in RID_LIST:
            if riddle['topic'] == topic:
                riddle['status'] = cmd
                finish_num = riddle['num']
                logging.info(f"auto/hint -> finish {finish_num}")
                # print('finish num', finish_num)
                for t in riddle['timers']:
                    if t.is_alive():
                        t.cancel()
                        logging.info(f"auto/hint -> riddle {riddle['num']} timer still alive -> kill timer")

        for riddle in RID_LIST:
            #find first biger erp_num
            if riddle['num'] > finish_num:
                logging.info(f"auto/hint -> find next riddle -> next {riddle['num']}")
                if riddle['autoi']:
                    logging.info(f"auto/hint -> riddle {riddle['num']} have auto hints")
                    if riddle['status'] != 'finish':
                        logging.info(f"auto/hint -> riddle {riddle['num']} have not realized timers -> star it")
                        for t in riddle['timers']:
                            t.start()
                else:
                    logging.info(f"auto/hint -> riddle {riddle['num']} have not auto hints, wait next finish")
                break;


def mqtt_routine(host, port):
    try:
        client.connect(host, port, 6)
        client.loop_start()
        logging.info(f"auto/hint/mqtt -> connect to {host}:{port}")
        while True:
            pass
    except socket.timeout:
        logging.info(f"auto/hint/mqtt -> did'n connect to {host}:{port} -> try again after 30 sec")
        time.sleep(30)
        mqtt_routine(host, port)
    except OSError:
        logging.info(f"auto/hint/mqtt -> network is unreachable -> try again after 30 sec")
        time.sleep(30)
        mqtt_routine(host, port)


mqtt_init(AUTO_SUBSCRIBE)
mqtt_routine(MQTT_HOST, MQTT_PORT)


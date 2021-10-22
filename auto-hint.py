import os
import django
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ers.settings")
django.setup()

import paho.mqtt.client as mqtt
from erp.tools import load_current_quest
import threading
import logging

MQTT_PORT = 1883
MQTT_HOST = "192.168.10.1"
TOPIC_OUT = "/er/async/auto/play"
SUBSCRIBE = []


RID_LIST = []
LN = None
client = None

def pub(name):
    client.publish(TOPIC_OUT, name)
    logging.debug(f"timer up, send file {name}")

def auto_hint_init():
    global SUBSCRIBE, LN, RID_LIST
    quest = load_current_quest()
    languages = quest.languages.split(',')
    LN = languages[quest.selected_language]
    quest_riddles = quest.riddel_set.all()
    SUBSCRIBE = ["/er/cmd", "/er/async"]
    RID_LIST = []

    #create RIDDLES datastract
    for r in quest_riddles:
        topic = f'/er/{r.erp_name}/cmd'
        SUBSCRIBE.append(topic)
        timers = []
        if r.autoi:
            cnt = 0
            for offset in r.autoi.split(','):
                timers.append(threading.Timer(int(offset), pub, [f"{r.erp_num+cnt}"]))
                cnt += 1
        RID_LIST.append({'num': r.erp_num, 'topic':topic, 'autoi': r.autoi,  'status': 'none', 'timers':timers})
    RID_LIST.sort(key=lambda x: x['num'])
    logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)
    print(RID_LIST)
    print("AUTO-HINT/Initiate:")


def auto_hint_manage(topic, cmd):
    print(topic, cmd)
    if topic == '/er/async' and cmd == 'reset':
        auto_hint_init()
    if topic == '/er/cmd' and cmd == 'start':
        if RID_LIST[0]['autoi']:
            for t in RID_LIST[0]['timers']:
                print('start FIRST RID timer')
                t.start()

    if cmd == 'finish':
        print('FINISH')
        for r in RID_LIST:
            if r['topic'] == topic:
                r['status'] = cmd
                finish_num = r['num']
                print('finish num', finish_num)
                for t in r['timers']:
                    if t.is_alive():
                        print(r['num'], 'timer still alive > kill')
                        t.cancel()

        for r in RID_LIST:
            #find first biger erp_num
            if r['num'] > finish_num:
                print('next num is ', r['num'])
                if r['autoi']:
                    print('riddle', r['num'], 'have auto hints')
                    if r['status'] != 'finish':
                        print('and have timers, start them')
                        for t in r['timers']:
                            t.start()
                else:
                    print('riddle', r['num'], 'have not auto hints, wait next finish')
                break;


def mqtt_init(topics):
    global client

    def on_connect(client, user_data, flags, rc):
        ignore = user_data
        ignore = flags
        for topic in topics:
            client.subscribe(topic)
            print(f"MQTT/Subscribe: {topic}")

    def on_message(client, userdata, message):
        cmd = message.payload.decode("utf-8")
        topic = message.topic
        print(f"MQTT/Received: {topic}/{cmd}")
        auto_hint_manage(topic, cmd)

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("MQTT/Disconnection:")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect


def mqtt_routine(host, port):
    client.connect(host, port, 6)
    client.loop_start()
    print(f"MQTT/Connecting: {host}:{port}")
    while True:
        pass


auto_hint_init()
mqtt_init(SUBSCRIBE)
mqtt_routine(MQTT_HOST, MQTT_PORT)

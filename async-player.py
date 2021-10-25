import os
import django
import paho.mqtt.client as mqtt
import threading
import logging

from os import getcwd
from os.path import join
from time import sleep
from mplayer import *

#neccessary for load data from model
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ers.settings")
django.setup()
from erp.tools import load_current_quest

#confign
MQTT_PORT = 1883
MQTT_HOST = "192.168.10.1"
SUBSCRIBE = [
    "/er/async/play",
    "/er/async/stop",
    "/er/async/reset",
    "/er/async/hint/play",
    "/er/async/auto/play",
    "/er/async/vol/set",

    "/er/music/play",
    "/er/music/stop",
    "/er/mc1/pause",
    "/er/mc1/resume",
    "/er/mc1/vol/set",

    "/er/musicback/play",
    "/er/musicback/stop",
    "/er/mc2/pause",
    "/er/mc2/resume",
    "/er/mc2/vol/set"]

#logging
LOGGING_PATH = "erserver.log"
LOGGING_LVL = logging.INFO

#paths
MEDIA_PATH =  "erp/media"
HINT_PATH = join(getcwd(), MEDIA_PATH, "hint/")
ACTION_PATH = join(getcwd(), MEDIA_PATH,"action/")
AUTO_PATH = join(getcwd(), MEDIA_PATH, "hint_auto/")
BACK_PATH = join(getcwd(), MEDIA_PATH, "background/")
DEFAULT_PATH = join(getcwd(), MEDIA_PATH, "default/")


#global vars
client = None
back_player = None
action_player = None
players = []
LN = ''
VOL = 20

# setup logging
logging.basicConfig(
    filename=LOGGING_PATH,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    level=LOGGING_LVL)


def load_ln():
    quest = load_current_quest()
    languages = quest.languages.split(',')
    return languages[quest.selected_language]


def load_vol():
    quest = load_current_quest()
    return quest.main_vol


def get_sound_path(path, ln, numb):
    # type check
    try:
        int(numb)
    except ValueError:
        logging.error(f"player -> wrong sound number {numb} -> number set 001")
        numb = '001'

    # range check
    if int(numb) < 1 or int(numb) > 260:
        logging.warning(f"player -> wrong sound number (1 <= x <= 260) {numb} -> number set 001")
        numb = '001'

    # len check
    while len(numb) != 3:
        numb = '0' + numb

    sound = list(filter(lambda s:s.startswith(f'|{numb}|{ln}|'), os.listdir(path)))
    if len(sound) == 1:
        logging.info(f"player -> find sound {sound[0]}")
        return path + sound[0]
    if len(sound) > 1:
        logging.warning(f"player -> find {len(names)} sound files: {names}")
        return path + sound[0]
    if len(sound) == 0:
        logging.warning(f"player -> dont find sound files with name |{numb}|{ln}|***.mp3")
        sound = list(filter(lambda s:s.startswith(f'{numb}'), os.listdir(path)))
        if len(sound) == 0:
            logging.warning(f"player -> dont find sound file with name {numb}***.mp3")
            sound = list(filter(lambda s:s.startswith(f'{numb}'), os.listdir(DEFAULT_PATH)))
            logging.warning(f"player -> find sound file {sound[0]} in default folder")
            return DEFAULT_PATH + sound[0]
        else:
            logging.warning(f"player -> find sound file {path + sound[0]} ")
            return path + sound[0]

def create_player(path, sound_numb, is_async):
    global players, LN
    class Player:
        def __init__(self, song_path, is_async):
            self._is_paused = False if is_async else True
            self._player = Player()
            self._player.volume = VOL
            self._player.loadfile(song_path)
            if not is_async:
                self._player.pause()

        def load(self, song_path):
            self._player.loadfile(song_path)
            self._is_paused = False

        def pause(self):
            if not self._is_paused:
                self._player.pause()
                self._is_paused = True

        def resume(self):
            if self._is_paused:
                self._player.pause()
                self._is_paused = False

        def set_volume(self, volume):
            if 0 <= volume <= 100:
                self._player.volume = volume

        def is_alive(self):
            return self._player.is_alive()

        def quit(self):
            self._player.quit()

    if is_async:
        new_player = Player(get_sound_path(path, LN, sound_numb), is_async=True)
        new_player.resume()

        #drop dead players
        for i in range(len(players)):
            if not players[i].is_alive():
                del players[i]

        players.append(new_player)
    else:
        return Player(get_sound_path(path, LN, sound_numb), is_async=False)


def init_music():
    global back_player, action_player, players, LN, VOL
    players = []
    LN = load_ln()
    VOL = load_vol()
    back_player = create_player(BACK_PATH, '001', is_async=False)
    action_player = create_player(ACTION_PATH, '001', is_async=False)
    logging.info(f"player -> initiate")
    action_player.resume()
    logging.info(f"player/action -> welcome sound")
    while True:
        pass


def mqtt_init(topics):
    global client

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logging.warning("player/mqtt -> disconnection")


    def on_connect(client, user_data, flags, rc):
        ignore = user_data
        ignore = flags
        for topic in topics:
            client.subscribe(topic)
            logging.info(f"player/mqtt -> subscribe on {topic}")

    def on_message(client, userdata, message):
        topic = message.topic
        arr = message.payload.decode("utf-8")
        manage_music(topic, arr)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect


def manage_music(topic, arr):
    global players, action_player, back_player, LN

    if topic == "/er/async/play":
        create_player(MEDIA_PATH, arr, is_async=True)
        logging.info(f"player/async -> play")

    if topic == "/er/async/hint/play":
        create_player(HINT_PATH, arr, is_async=True)
        logging.info(f"player/async/hint -> play")

    if topic == "/er/async/auto/play":
        create_player(AUTO_PATH, arr, is_async=True)
        logging.info(f"player/async/auto -> play")

    if topic == "/er/async/stop":
        for player in players:
            player.pause()
        logging.info(f"player/async -> stop")

    if topic == "/er/async/reset":
        LN = load_ln()
        players = []
        logging.info(f"player/async -> reset")

    if topic == "/er/music/play":
        action_player.load(get_sound_path(ACTION_PATH, LN, arr))
        logging.info(f"player/action -> play")

    if topic == "/er/music/stop" or topic == "/er/mc1/pause":
        action_player.pause()
        logging.info(f"player/action -> pause")

    if  topic == "/er/mc1/resume":
        action_player.resume()

    if topic == "/er/musicback/play":
        back_player.load(get_sound_path(BACK_PATH, LN, arr))
        logging.info(f"player/back -> play")

    if  topic == "/er/mc2/resume":
        back_player.resume()
        logging.info(f"player/back -> play")

    if topic == "/er/musicback/stop" or topic == "/er/mc2/pause":
        back_player.pause()
        logging.info(f"player/back -> stop")

    if topic == "/er/mc1/vol/set":
        action_player.set_volume(int(arr))
        logging.info(f"player/action/vol -> set {arr}")

    if topic == "/er/mc2/vol/set":
        back_player.set_volume(int(arr))
        logging.info(f"player/back/vol -> set {arr}")

    if topic == "/er/async/vol/set":
        for player in players:
            player.set_volume(int(arr))
        logging.info(f"player/async/vol -> set {arr}")

def mqtt_routine(host, port):
    client.connect(host, port, 6)
    client.loop_start()
    logging.info(f"player/mqtt -> connect to {host}:{port}")


mqtt_init(SUBSCRIBE)
mqtt_routine(MQTT_HOST, MQTT_PORT)
sleep(.1)
init_music()

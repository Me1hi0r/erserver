import os
import django
from os import getcwd
from os.path import join
from time import sleep
import paho.mqtt.client as mqtt
import threading
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ers.settings")
django.setup()
from erp.tools import load_current_quest
from mplayer import *

#confign
MQTT_PORT = 1883
MQTT_HOST = "192.168.10.1"
DEFAULT_BACK = '001_back.mp3'
DEFAULT_SYSTEM = '001_welcome.mp3'
LOGGING_PATH = "erserver.log"
MEDIA_PATH =  "erp/media"
BACK_PATH = join(getcwd(), MEDIA_PATH, "back/")
HINT_PATH = join(getcwd(), MEDIA_PATH, "hint/")
AUTO_PATH = join(getcwd(), MEDIA_PATH, "auto/")
ACTION_PATH = join(getcwd(), MEDIA_PATH,"action/")
SYSTEM_PATH = join(getcwd(), MEDIA_PATH,"system/")
DEFAULT_PATH = join(getcwd(), MEDIA_PATH, "base/")

LOGGING_LVL = logging.INFO
SUBSCRIBE = [
    "/er/async/reset",
    "/er/async/play",
    "/er/async/hint/play",
    "/er/async/auto/play",
    "/er/async/stop",
    "/er/music/play",
    "/er/music/stop",
    "/er/musicback/play",
    "/er/musicback/stop",
    "/er/mc1/pause",
    "/er/mc1/resume",
    "/er/mc1/vol/set",
    "/er/mc2/pause",
    "/er/mc2/resume",
    "/er/mc2/vol/set"]


#global variable
client = None
back_player = None
action_player = None
players = []
LN = ''
VOL = 60

# setup logging
logging.basicConfig(
    filename=LOGGING_PATH,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    level=LOGGING_LVL)

# def get_name(sound_num, sound_type, sound_lang):
#   num = sound_num if len(sound_num) == 3 else '0' + sound_num
#   path = join(getcwd(), MEDIA_PATH, sound_type)
#   print(path)

# def reset_music():
#   global LN
#   quest = load_current_quest()
#   languages = quest.languages.split(',')
#   LN = languages[quest.selected_language]

def load_ln():
    quest = load_current_quest()
    languages = quest.languages.split(',')
    return languages[quest.selected_language]

def load_vol():
    quest = load_current_quest()
    return quest.main_vol

def sound_path(path, ln, numb):
    try:
        int(numb)
    except ValueError:
        logging.error(f"player -> wrong sound number {numb}, number set 001")
        numb = '001'
    if int(numb) < 1 or int(numb) > 260:
        logging.warning(f"player -> wrong sound number {numb}, number set 001")
        numb = '001'
    while len(numb) != 3:
        numb = '0' + numb
    sound = list(filter(
        lambda s:s.startswith(f'|{numb}|{ln}|'),
        os.listdir(path)))
    if len(sound) == 1:
        logging.info(f"player -> find sound {sound[0]}")
        return path + sound[0]
    if len(sound) > 1:
        logging.warning(f"player -> find {len(names)} sound files: {names}")
        return path + sound[0]
    if len(sound) == 0:
        logging.warning(f"player -> dont find sound files with {numb} and {ln}")
        sound = list(filter(
            lambda s:s.startswith(f'{numb}'), os.listdir(DEFAULT_PATH)))
        logging.warning(f"player -> find default sound files {sound[0]}")
        return DEFAULT_PATH + sound[0]

def async_play(path, ln, arr):
    global players
    class AsyncPlayerDecorator:
        def __init__(self, song_path):
            self._is_paused = False
            self._player = Player()
            self._player.volume = VOL
            self._player.loadfile(song_path)
            # self._player.pause()

        def load(self, song_path):
            # print("load path" , soug_path)
            self._player.loadfile(song_path)
            self._is_paused = False

        # def load_cwd(self, song_name):
        #     print("start playing: " + join(getcwd(), MEDIA_PATH, song_name))
        #     self.load(join(getcwd(), MEDIA_PATH, song_name))

        def pause(self):
            if not self._is_paused:
                self._player.pause()
                self._is_paused = True

        def resume(self):
            if self._is_paused:
                self._player.pause()
                self._is_paused = False

        def set_volume(self, volume):
            # print("volume: ", volume)
            if 0 <= volume <= 100:
                self._player.volume = volume

        def is_alive(self):
            return self._player.is_alive()

        def quit(self):
            self._player.quit()


    new_player = AsyncPlayerDecorator(sound_path(HINT_PATH, LN, arr))
    new_player.resume()

    #drop dead players
    for i in range(len(players)):
        if not players[i].is_alive():
            del players[i]

    players.append(new_player)


def init_music():
    global back_player, action_player, players, LN, VOL
    players = []
    LN = load_ln()
    VOL = load_vol()
    back_player = PlayerDecorator(BACK_PATH + DEFAULT_BACK)
    action_player = PlayerDecorator(SYSTEM_PATH + DEFAULT_SYSTEM)
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
        async_play(MEDIA_PATH, LN, arr)
        logging.info(f"player/async -> play")

    if topic == "/er/async/hint/play":
        async_play(HINT_PATH, LN, arr)
        logging.info(f"player/async/hint -> play")

    if topic == "/er/async/auto/play":
        async_play(AUTO_PATH, LN, arr)
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
        # arr = arr if len(arr) == 3 else '0' + arr
        # path = join(getcwd(), MEDIA_PATH, 'system')
        # print(path)
        # sound_name = list(filter(lambda s:s.startswith(f'|{arr}|{LN}|'), os.listdir(path)))[0]
        # sound_name = list(filter(lambda s:s.startswith(f'|{arr}|{LN}|'), os.listdir(path)))
        # print(sound_name)
        action_player.load(sound_path(ACTION_PATH, LN, arr))
        logging.info(f"player/action -> play")

    if topic == "/er/music/stop" or topic == "/er/mc1/pause":
        action_player.pause()
        logging.info(f"player/action -> pause")

    if topic == "/er/music/play" or topic == "/er/mc1/resume":
        action_player.resume()

    if topic == "/er/musicback/play" or topic == "/er/mc2/resume":
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


def mqtt_routine(host, port):
    client.connect(host, port, 6)
    client.loop_start()
    logging.info(f"player/mqtt -> connect to {host}:{port}")

class PlayerDecorator:
    def __init__(self, song_path):
        self._is_paused = True
        self._player = Player()
        self._player.volume = VOL
        self._player.loadfile(song_path)
        self._player.pause()

    def load(self, song_path):
        # print("load path" , song_path)
        self._player.loadfile(song_path)
        self._is_paused = False

    # def load_cwd(self, song_name):
    #     print("start playing: " + join(getcwd(), MEDIA_PATH, song_name))
    #     self.load(join(getcwd(), MEDIA_PATH, song_name))

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



mqtt_init(SUBSCRIBE)
mqtt_routine(MQTT_HOST, MQTT_PORT)
sleep(.1)
init_music()

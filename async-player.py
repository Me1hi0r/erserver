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
MEDIA_PATH =  "erp/media"
BACK_PATH = join(getcwd(), MEDIA_PATH, "back/")
SYSTEM_PATH = join(getcwd(), MEDIA_PATH,"system/")
HINT_PATH = join(getcwd(), MEDIA_PATH, "hint/")
DEFAULT_BACK = '001_back.mp3'
DEFAULT_SYSTEM = '001_welcome.mp3'
LOGGING_PATH = "erserver.log"

LOGGING_LVL = logging.INFO
SUBSCRIBE = [
    "/er/async",
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
back_music = ""
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

#   logging.info(f"player -> get {sound_lang}{sound_type}{sound_num}")
#   sound_name = list(filter(lambda s:s.startswith(f'|{num}|{sound_lang}|'), os.listdir(path)))[0]
#   return sound_name

# def reset_music():
#   global LN
#   quest = load_current_quest()
#   languages = quest.languages.split(',')
#   LN = languages[quest.selected_language]

def init_music():
    global back_music, back_player, action_player, players, LN, VOL
    quest = load_current_quest()
    VOL = quest.main_vol
    languages = quest.languages.split(',')
    LN = languages[quest.selected_language]
    players = []
    logging.info(f"player -> initiate")
    back_player = PlayerDecorator(BACK_PATH + DEFAULT_BACK)
    action_player = PlayerDecorator(SYSTEM_PATH + DEFAULT_SYSTEM)
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
    if topic == "/er/async" and arr == 'reset':
        quest = load_current_quest()
        languages = quest.languages.split(',')
        LN = languages[quest.selected_language]
        for i in range(len(players)):
            del players[i]
        players = []
        logging.info(f"player/async -> reset")


    if topic == "/er/async/hint/play":
        path = join(getcwd(), MEDIA_PATH, 'hint')
        print(path)
        sound_name = list(filter(lambda s:s.startswith(f'|{arr}|{LN}|'), os.listdir(path)))[0]
        print(sound_name)
        for i in range(len(players)):
            if not players[i].is_alive():
                del players[i]
        # print(path+sound_name)

        new_player = AsyncPlayerDecorator(join(path,sound_name))
        new_player.resume()
        players.append(new_player)

    if topic == "/er/async/auto/play":
        path = join(getcwd(), MEDIA_PATH, 'auto')

        arr = arr if len(arr) == 3 else '0' + arr
        sound_name = list(filter(lambda s:s.startswith(f'|{arr}|{LN}|'), os.listdir(path)))[0]
        for i in range(len(players)):
            if not players[i].is_alive():
                del players[i]

        new_player = AsyncPlayerDecorator(join(path,sound_name))
        new_player.resume()
        players.append(new_player)

    if topic == "/er/async/play":
        for i in range(len(players)):
            if not players[i].is_alive():
                del players[i]
        new_player = AsyncPlayerDecorator(join(getcwd(), MEDIA_PATH, arr))
        new_player.resume()
        players.append(new_player)


    if topic == "/er/async/stop":
        for player in players:
            player.pause()
        players = []

    if topic == "/er/music/play":
        arr = arr if len(arr) == 3 else '0' + arr
        path = join(getcwd(), MEDIA_PATH, 'system')
        print(path)
        # sound_name = list(filter(lambda s:s.startswith(f'|{arr}|{LN}|'), os.listdir(path)))[0]
        sound_name = list(filter(lambda s:s.startswith(f'|{arr}|{LN}|'), os.listdir(path)))
        print(sound_name)
        action_player.load(join(path,sound_name))

    if topic == "/er/music/stop":
        action_player.pause()

    if topic == "/er/musicback/play":
        back_player.resume()

    if topic == "/er/musicback/stop":
        back_player.pause()

    if topic == "/er/mc1/pause":
        action_player.pause()

    if topic == "/er/mc1/resume":
        action_player.resume()

    if topic == "/er/mc1/vol/set":
        action_player.set_volume(int(arr))

    if topic == "/er/mc2/vol/set":
        back_player.set_volume(int(arr))

    if topic == "/er/mc2/pause":
        back_player.pause()

    if topic == "/er/mc2/resume":
        back_player.resume()




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
        print("load path" , song_path)
        self._player.loadfile(song_path)
        self._is_paused = False

    def load_cwd(self, song_name):
        print("start playing: " + join(getcwd(), MEDIA_PATH, song_name))
        self.load(join(getcwd(), MEDIA_PATH, song_name))

    def pause(self):
        if not self._is_paused:
            self._player.pause()
            self._is_paused = True

    def resume(self):
        if self._is_paused:
            self._player.pause()
            self._is_paused = False

    def set_volume(self, volume):
        print("volume: ", volume)
        if 0 <= volume <= 100:
            self._player.volume = volume

    def is_alive(self):
        return self._player.is_alive()

    def quit(self):
        self._player.quit()


class AsyncPlayerDecorator:
    def __init__(self, song_path):
        self._is_paused = False

        self._player = Player()
        self._player.volume = VOL
        self._player.loadfile(song_path)
        # self._player.pause()

    def load(self, song_path):
        print("load path" , soug_path)
        self._player.loadfile(song_path)
        self._is_paused = False

    def load_cwd(self, song_name):
        print("start playing: " + join(getcwd(), MEDIA_PATH, song_name))
        self.load(join(getcwd(), MEDIA_PATH, song_name))

    def pause(self):
        if not self._is_paused:
            self._player.pause()
            self._is_paused = True

    def resume(self):
        if self._is_paused:
            self._player.pause()
            self._is_paused = False

    def set_volume(self, volume):
        print("volume: ", volume)
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

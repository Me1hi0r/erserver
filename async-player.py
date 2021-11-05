import os
import time
import django
import socket
import logging
import threading
from mplayer import *
import paho.mqtt.client as mqtt

#neccessary for load data from model
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()
from panel.tools import load_ln, load_vol
from server.settings import MQTT_PORT, MQTT_HOST, PLAYER_SUBSCRIBE, MEDIA_PATH, ACTION_PATH, AUTO_PATH, BACK_PATH, DEFAULT_PATH, HINT_PATH


#global vars
client = None
back_player = None
action_player = None
players = []
LN = ''
VOL = 20


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
    class CustomPlayer:
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
        new_player = CustomPlayer(get_sound_path(path, LN, sound_numb), is_async=True)
        new_player.resume()

        #drop dead players
        for i in range(len(players)):
            if not players[i].is_alive():
                del players[i]

        players.append(new_player)
    else:
        return CustomPlayer(get_sound_path(path, LN, sound_numb), is_async=False)

def init_players():
    global action_player, back_player
    back_player = create_player(BACK_PATH, '001', is_async=False)
    action_player = create_player(ACTION_PATH, '001', is_async=False)
    logging.info(f"player -> initiate")
    action_player.resume()

def init_music():
    global back_player, action_player, players, LN, VOL
    players = []
    LN = load_ln()
    VOL = load_vol()
    init_players()
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
        msg = message.payload.decode("utf-8")
        manage_music(topic, msg)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect


def manage_music(topic, numb):
    global players, action_player, back_player, LN

    if topic == "/er/async/play":
        create_player(MEDIA_PATH, numb, is_async=True)
        logging.info(f"player/async -> play")

    if topic == "/er/async/hint/play":
        create_player(HINT_PATH, numb, is_async=True)
        logging.info(f"player/async/hint -> play")

    if topic == "/er/async/auto/play":
        create_player(AUTO_PATH, numb, is_async=True)
        logging.info(f"player/async/auto -> play")

    if topic == "/er/async/stop":
        for player in players:
            player.pause()
        logging.info(f"player/async -> stop")

    if topic == "/er/async/reset":
        action_player.quit()
        back_player.quit()

        for p in players:
            p.quit()
        players = []
        logging.info(f"player/async -> reset")
        init_players()

    if topic == "/er/music/play":
        action_player.load(get_sound_path(ACTION_PATH, LN, numb))
        logging.info(f"player/action -> play")

    if topic == "/er/music/stop" or topic == "/er/mc1/pause":
        action_player.pause()
        logging.info(f"player/action -> pause")

    if  topic == "/er/mc1/resume":
        action_player.resume()

    if topic == "/er/musicback/play":
        back_player.load(get_sound_path(BACK_PATH, LN, numb))
        logging.info(f"player/back -> play")

    if  topic == "/er/mc2/resume":
        back_player.resume()
        logging.info(f"player/back -> play")

    if topic == "/er/musicback/stop" or topic == "/er/mc2/pause":
        back_player.pause()
        logging.info(f"player/back -> stop")

    if topic == "/er/mc1/vol/set":
        action_player.set_volume(int(numb))
        logging.info(f"player/action/vol -> set {numb}")

    if topic == "/er/mc2/vol/set":
        back_player.set_volume(int(numb))
        logging.info(f"player/back/vol -> set {numb}")

    if topic == "/er/async/vol/set":
        for player in players:
            player.set_volume(int(numb))
        logging.info(f"player/async/vol -> set {numb}")

def mqtt_routine(host, port):
    try:
        client.connect(host, port, 6)
        client.loop_start()
        logging.info(f"player/mqtt -> connect to {host}:{port}")
    except socket.timeout:
        logging.info(f"player/mqtt -> did'n connect to {host}:{port} -> try again after 30 sec")
        time.sleep(30)
        mqtt_routine(host, port)
    except OSError:
        logging.info(f"player/mqtt -> network is unreachable -> try again after 30 sec")
        time.sleep(30)
        mqtt_routine(host, port)



mqtt_init(PLAYER_SUBSCRIBE)
mqtt_routine(MQTT_HOST, MQTT_PORT)
time.sleep(.1)
init_music()

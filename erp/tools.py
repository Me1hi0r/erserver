from erp.models import Panel, Quest
from ers.settings import BASE_DIR, os
from shutil import copy2, copyfile
from os import listdir
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from openpyxl import Workbook
from openpyxl.utils.datetime import to_excel
from datetime import datetime, timezone

# from erp.models import Statistic


def for_each(arr):
    out_arr = arr
    for e in out_arr:
        e['sound_buttons'] = [numb+1 for numb in range(int(e['sound_buttons']))]
        e['video_buttons'] = [numb+1 for numb in range(int(e['video_buttons']))]
    return out_arr

def load_current_quest():
    name = Panel.objects.get(pk=1).quest
    return Quest.objects.get(name=name)

def set_current_quest(name):
    panel = Panel.objects.get(pk=1)
    panel.quest = name
    panel.save()

def sorted_riddles():
    q = load_current_quest()
    quest_riddles = q.riddel_set.all()
    return sorted(quest_riddles, key=lambda riddle: riddle.panel_order)

def quest_languages():
    q = load_current_quest()
    return q.languages.split(',')

def only_langs_sound(sound_type):
    return list(filter(lambda s:s.startswith('|'), os.listdir(sound_type)))

def only_base_sound(sound_type):
    return list(filter(lambda s: not s.startswith('|'), os.listdir(sound_type)))


def load_langs():
    q = load_current_quest()
    return q.languages.split(',')

def load_select_lang():
    q = load_current_quest()
    languages = q.languages.split(',')
    return languages[q.selected_language]


def load_ln():
    quest = load_current_quest()
    languages = quest.languages.split(',')
    return languages[quest.selected_language]


def load_vol():
    quest = load_current_quest()
    return quest.main_vol



def quest_riddles():
    quest = load_current_quest()
    return quest.riddel_set.all()


def str_time(sec):
    m = str(sec // 60)
    s = str(sec % 60)
    if len(s) == 1:
        s = '0' + s
    return f"{m}:{s}"


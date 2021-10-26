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

from erp.models import Statistic


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


#+++++++MAIL
def obj_to_xlsx():
    stat = Statistic.objects.all()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Statistic'
    col = ['day', 'time', 'status']
    rown = 1

    for col_num, col_title in enumerate(col,1):
        cell = ws.cell(row=rown, column=col_num)
        cell.value = col_title
    for s in stat:
        rown += 1
        # row = [s.time, s.status]
        s.time
        row = [f'{s.time.month}-{s.time.day}', f'{s.time.hour}:{s.time.minute}',s.status]
        for col_num, cell_value in enumerate(row, 1):
            cell = ws.cell(row=rown, column=col_num)
            cell.value = cell_value
    wb.save('stat.xlsx')


def send_mail():
    sender_email = "grilitovchenko@gmail.com"
    receiver_email = "grilitovchenko@gmail.com"
    # password = input("Type your password and press enter:")
    password = "BdFQRR6aad4b5ci"
    message = """ Subject: Hi there
    This message is sent from Python."""


    msg = MIMEMultipart()
    # storing the senders email address
    msg['From'] = sender_email
    # storing the receivers email address
    msg['To'] = sender_email
    # storing the subject
    msg['Subject'] = "Subject of the Mail"
    # string to store the body of the mail
    body = "Body_of_the_mail"
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    # open the file to be sent
    filename = "stat.xlsx"
    obj_to_xlsx()
    attachment = open("/home/melhior/projects/Python/ers-rasp/stat.xlsx", "rb")
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    # encode into base64
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(sender_email,password)
    server.sendmail(sender_email,sender_email,text)
    print("Mail Send Successfully")
    server.quit()


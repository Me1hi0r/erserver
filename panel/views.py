import os
import json
import logging
import operator
from functools import reduce
# from os.sound_folder import join
from shutil import copy2, copyfile
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from server.settings import BASE_DIR, MEDIA_ROOT, DEFAULT_DIR,os
from panel.models import Panel, Quest, Riddel
from panel.tools import for_each,  load_current_quest, set_current_quest
from panel.tools import sorted_riddles, quest_languages, only_langs_sound
from panel.tools import only_base_sound, load_langs, load_select_lang



def log_in(request):
    if request.user.is_authenticated:
        logging.info(f"panel -> user {request.user} is authenticated")
        return HttpResponseRedirect("/panel")
    logging.info(f"panel -> user {request.user} is not authenticated")
    return render(request, "login.html", {})

def authentification(request, action):
    if action == 'login':
        return HttpResponseRedirect("/")
    if action == 'logout':
        logout(request)
        return HttpResponseRedirect("/")
    if action == 'check':
        data = json.loads(request.body.decode("utf-8"))
        user = authenticate(request, username=data['name'], password=data['pass'])
        if user is not None:
            login(request, user)
            logging.info(f"panel -> user {user} is authenticated and login")
            return JsonResponse({'status': 'user-authentification'})
        else:
            logging.info(f"panel -> user {user} not exist")
            return JsonResponse({'status': 'user-not-exist'})

@login_required()
def debug(request):
    return render(request, "debug.html", {})

@login_required()
def panel(request):
    return render(request, "panel.html", {
        'quest_riddles': sorted_riddles()
    })

@login_required()
def sound(request):
    return render(request, "sound.html", {
        'quest_riddles': sorted_riddles()
    })

@login_required()
def config(request, action=''):
    if request.method == 'GET':
        q = load_current_quest()
        all_other_quest = Quest.objects.all().exclude(name=q.name)

        return render(request, "config.html", {
            'quest_name': q.name,
            'quest_riddles': sorted_riddles(),
            'all_other_quest': all_other_quest,
            'playing_time': q.playing_time,
            'start_offset': q.start_offset,
            'main_vol': q.main_vol,
            'back_vol': q.back_vol,
            'show_dificult': q.show_dificult,
            'selected_dificult': q.selected_dificult,
            'show_autohints': q.show_autohints,
            'show_languages': q.show_languages,
            'show_audio_hints': q.show_audio_hints,
            'show_video_hints': q.show_video_hints,
            'show_start_offset': q.show_start_offset,
            'languages': q.languages,
            'selected_language': q.selected_language,
            'separate_languages': load_langs()})

    if request.method == 'POST' and action == 'new':
        name = request.POST.get('new-quest-name')
        new_quest = Quest.objects.create(name=name)
        new_quest.save()
        set_current_quest(name)
        logging.info(f"panel/config -> create new configuration of quest {name} and set it")
        return HttpResponseRedirect("/config")

    if request.method == 'POST' and action == 'load':
        name = request.POST.get('load-quest-name')
        set_current_quest(name)
        logging.info(f"panel/config -> load configuration of quest {name}")
        return HttpResponseRedirect("/config")

    if request.method == 'POST' and action == 'save':
        # update all changes in quest
        q = load_current_quest()
        q.show_autohints = bool(request.POST.get('show_autohints'))
        q.languages = request.POST.get('languages')
        q.main_vol = request.POST.get('main_vol')
        q.back_vol = request.POST.get('back_vol')
        q.show_languages = bool(request.POST.get('show_languages'))
        q.show_dificult = bool(request.POST.get('show_dificult'))
        q.show_audio_hints = bool(request.POST.get('show_audio_hints'))
        q.show_video_hints = bool(request.POST.get('show_video_hints'))
        q.show_start_offset = bool(request.POST.get('show_start_offset'))
        q.selected_dificult = request.POST.get('selected_dificult')
        q.selected_language = request.POST.get('selected_language')
        q.start_offset = request.POST.get('start_offset')
        q.playing_time = request.POST.get('playing_time')
        q.save()

        # update all changes in any riddels
        rid_count = int(request.POST.get('rid-count'))
        fields_name = [f.name for f in Riddel._meta.get_fields()]
        rid = dict.fromkeys(fields_name)
        rid['autoi'] = ''
        RIDDELS = [dict(rid) for _ in range(rid_count)]

        for key, val in request.POST.items():
            if key.startswith('riddle') and key.find('autoi') != -1:
                [_, number, f, an] = key.split("-")
                RIDDELS[int(number)-1][f] += val + ','
            elif key.startswith('riddle'):
                [_, number, f] = key.split("-")
                RIDDELS[int(number)-1][f] = val
        for rid in RIDDELS:
            riddle = q.riddel_set.get(erp_num=int(rid['erpnum']))
            riddle.panel_order = int(rid['order'])
            riddle.erp_name = rid['id']
            riddle.panel_name = rid['name']
            riddle.video_hints = rid['video_buttons']
            old_sound_hints = riddle.sound_hints
            riddle.sound_hints = rid['sound_buttons']
            old_auto_hints = riddle.auto_hints
            riddle.autoi = rid['autoi'][0:-1] if rid['autoi'] else ''
            riddle.auto_hints = rid['auto_buttons']
            riddle.save()
            add_or_del_sounds(riddle.sound_hints, old_sound_hints, riddle.erp_num,'hint')
            add_or_del_sounds(riddle.auto_hints, old_auto_hints, riddle.erp_num,'hint_auto')
            logging.info(f"panel/config -> update sound hint and auto_hint")
        logging.info(f"panel/config -> save configuration")

        return HttpResponseRedirect("/config")

@login_required()
def upload_sound(request):
    if request.method == "POST":
        file = request.FILES["file"]
        sound_type = request.POST["type"]
        old_name = request.POST["old_name"]

        os.remove(f'{MEDIA_ROOT}{sound_type}/{old_name}')

        new_name = old_name[0:8] + file.name.replace(" ", "")
        with open(f'{MEDIA_ROOT}{sound_type}/{new_name}', 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    logging.info(f"panel -> upload sound")
    return HttpResponseRedirect("sound")

@login_required()
def sound_list(request, sound_type, riddle=0):
    if request.method == "GET":
        sound = []
        for track in only_langs_sound(f'{MEDIA_ROOT}{sound_type}/'):
            _, numb, sound_lang, _ = track.split("|")
            numb = int(numb)
            if numb >= riddle and numb < riddle+10 and sound_lang == load_select_lang():
                sound.append(track)
        logging.info(f"panel -> generate sound list")
        return JsonResponse({"sounds": sound})

@login_required()
def reset_sound(request):
    if request.method == 'POST':
        print("DELETE ALL LANG SOUND")
        for sound_type in ['action', 'hint', 'hint_auto', 'background']:
            type_folder = f'{MEDIA_ROOT}{sound_type}/'
            langs_sound = only_langs_sound(type_folder)
            # for sound in not_use_lang_sound_list(langs_sound, load_langs()):
            for sound in only_langs_sound(type_folder):
                os.remove(f'{type_folder}{sound}')

        print("CREATE NEW LANG SOUND")
        for riddle in sorted_riddles():
            add_or_del_sounds(riddle.auto_hints, 0, riddle.erp_num, 'hint_auto')
            add_or_del_sounds(riddle.sound_hints, 0, riddle.erp_num, 'hint')

        for sound_type in ['action', 'background']:
            for sound in only_base_sound(MEDIA_ROOT + f'{sound_type}/'):
                number, name = sound.split("_", 1)
                fr = f'{MEDIA_ROOT}{sound_type}/{sound}'
                for language in load_langs():
                    to = f'{MEDIA_ROOT}{sound_type}/|{number}|{language}|{name}'
                    copyfile(fr, to)

        logging.info(f"panel/sound-managment -> reset all sounds")
        return HttpResponseRedirect("/sound")


def add_or_del_sounds(new, old, num, sound_type):
    new, old, num = list(map(int, [new, old, num]))
    diff = new - old

    if(diff > 0):
        for i in range(old, new):
            number = str(num + i)
            number = number if len(number) == 3 else '0' + number
            i = str(int(number[2]) + 1)
            fr = f'{DEFAULT_DIR}{number}.mp3'
            for ln in quest_languages():
                to = f'{MEDIA_ROOT}{sound_type}/|{number}|{ln}|{sound_type}_{i}.mp3'
                copyfile(fr, to)
        logging.info(f"panel/sound-managment -> copy {diff} stub sound in {sound_type} sound_type")

    if(diff < 0):
        for sound in only_langs_sound(MEDIA_ROOT + f'{sound_type}/'):
            for number in range(new, old):
                if str(number + num) in sound:
                    os.remove(MEDIA_ROOT + f'{sound_type}/' + sound)
        logging.info(f"panel/sound-managment -> delete {-diff} sound in {sound_type} sound_type")


#++++++++++++++MAIL++++++++++++++++++++++++++++++++++++
# def report(request):
#     if request.method == "GET":
#         json = {"status": "mail"}
#         send_mail()
#     return JsonResponse(json)

#-----------------DATA----------------------------------
def data(request):
    if request.method == "GET":
        # print("DATA")
        q = load_current_quest()
        rn = len( q.riddel_set.all())
        json = {}
        json.update({
            'quest_name': q.name,
            'rid_num': rn,
            'sound_main': q.main_vol,
            'sound_back': q.back_vol,
            'timer_offset': q.start_offset,
            'timer_walk': q.playing_time,
            'dificult': q.selected_dificult,
            'language': q.selected_language,
            'riddles': {},
        })
        for number, rid in zip(range(rn), q.riddel_set.all()):
            json['riddles'][number] = {'strId': rid.erp_name, 'strName': rid.panel_name, 'strStatus':"Not activated", 'number': rid.erp_num, 'sound_buttons': rid.sound_hints, 'video_buttons': rid.video_hints}
        # print(json)
    return JsonResponse(json)


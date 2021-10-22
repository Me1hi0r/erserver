from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist

from shutil import copy2, copyfile
from erp.models import Panel, Statistic, Quest, Riddel
from erp.tools import for_each, send_mail, load_current_quest, set_current_quest
from ers.settings import BASE_DIR, os

import os
from os.path import join
import json

def log_in(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/panel")
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
            return JsonResponse({'status': 'user-authentification'})
        else:
            return JsonResponse({'status': 'user-not-exist'})

@login_required()
def panel(request):
    q = load_current_quest()
    quest_riddles = q.riddel_set.all()
    sorted_rid = sorted(quest_riddles, key=lambda r: r.panel_order)

    return render(request, "panel.html", {
        # 'quest_riddles': quest_riddles,
        'quest_riddles': sorted_rid,
    })


@login_required()
def config(request, action=''):
    if request.method == 'GET':
        q = load_current_quest()
        quest_riddels = q.riddel_set.all()
        sorted_rid = sorted(quest_riddels, key=lambda r: r.panel_order)
        all_other_quest = Quest.objects.all().exclude(name=q.name)
        separate_languages = q.languages.split(",")

        return render(request, "config.html", {
            'quest_name': q.name,
            'quest_riddles': sorted_rid,
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
            'separate_languages': separate_languages})

    if request.method == 'POST' and action == 'new':
        name = request.POST.get('new-quest-name')
        new_quest = Quest.objects.create(name=name)
        new_quest.save()
        set_current_quest(name)
        return HttpResponseRedirect("/config")

    if request.method == 'POST' and action == 'load':
        name = request.POST.get('load-quest-name')
        set_current_quest(name)
        return HttpResponseRedirect("/config")

    if request.method == 'POST' and action == 'save':
        # update quest
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

        # create or/and update all riddels
        rid_count = int(request.POST.get('rid-count'))
        fields_name = [f.name for f in Riddel._meta.get_fields()]
        rid = dict.fromkeys(fields_name)
        rid['autoi'] = ''
        RIDDELS = [dict(rid) for _ in range(rid_count)]

        for key, val in request.POST.items():
            if key.startswith('riddle') and key.find('autoi') != -1:
                [_, n, f, an] = key.split("-")
                RIDDELS[int(n)-1][f] += val + ','
            elif key.startswith('riddle'):
                [_, n, f] = key.split("-")
                RIDDELS[int(n)-1][f] = val
        for rid in RIDDELS:
            try:
                r = q.riddel_set.get(erp_num=int(rid['erpnum']))
                r.panel_order = int(rid['order'])
                r.erp_name = rid['id']
                r.panel_name = rid['name']
                r.video_hints = rid['video_buttons']
                old_sound_hints = r.sound_hints
                r.sound_hints = rid['sound_buttons']
                old_auto_hints = r.auto_hints
                r.autoi = rid['autoi'][0:-1] if rid['autoi'] else ''
                r.auto_hints = rid['auto_buttons']
                r.save()

                add_or_del_sounds(r.sound_hints, old_sound_hints, r.erp_num,'hint')
                add_or_del_sounds(r.auto_hints, old_auto_hints, r.erp_num,'auto')

            except ObjectDoesNotExist:
                r = Riddel.objects.create(
                    quest = q,
                    panel_order = int(rid['order']),
                    erp_name = rid['id'],
                    erp_num = int(rid['erpnum']),
                    panel_name = rid['name'],
                    sound_hints = rid['sound_buttons'],
                    video_hints = rid['video_buttons'],
                    auto_hints = rid['auto_buttons'],
                    autoi = rid['autoi'][0:-1] if rid['autoi'] else 0
                    )
                r.save()
        return HttpResponseRedirect("/config")

@login_required()
def sound(request):
    q = load_current_quest()
    quest_riddles = q.riddel_set.all()

    return render(request, "sound.html", {
        'quest_riddles': quest_riddles,
    })

def upload_sound(request):
    if request.method == "POST":
        file = request.FILES["file"]
        sound_type = request.POST["type"]
        old_name = request.POST["old_name"]

        old_track_path = join(BASE_DIR, f'erp/media/{sound_type}/{old_name}')
        print(old_track_path)
        os.remove(old_track_path)

        prefix = old_name[0:4] if(sound_type == "back" or sound_type == "system") else old_name[0:8]
        new_name = prefix + file.name.replace(" ", "")
        new_track_path = join(BASE_DIR, f'erp/media/{sound_type}/{new_name}')
        print(new_track_path)
        with open(new_track_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    return HttpResponseRedirect("sound")


def sound_list(request, sound_type, riddle=0):
    print("LIST")

    q = load_current_quest()
    languages = q.languages.split(',')
    current_language = languages[q.selected_language]

    if request.method == "GET":
        sound = []
        for track in os.listdir(f"erp/media/{sound_type}/"):
            if track.startswith("|"):
                if (sound_type == "system" or sound_type == "back"):
                    sound.append(track)
                if (sound_type == "action" or sound_type == "hint" or sound_type == 'auto'):
                    _, numb, sound_lang, _ = track.split("|")
                    sound_numb = int(numb)
                    if sound_numb >= riddle and sound_numb < riddle+10 and sound_lang == current_language:
                        sound.append(track)
        print(sound)
        return JsonResponse({"sounds": sound})




def reset_sound(request):
    if request.method == 'POST':
        manage_all_sound()
        return HttpResponseRedirect("/sound")


def add_or_del_sounds(new, old, num, t):
    new = int(new)
    old = int(old)
    num = int(num)
    q = load_current_quest()
    path = join(BASE_DIR, f'erp/media/{t}/')
    diff = new - old

    if(diff > 0):
        # print('COPY FILES')
        for c, n in enumerate(range(diff)):
            n = str(num + n)
            n = n if len(n) == 3 else '0' + n
            fr = join(BASE_DIR, f'erp/media/{t}/', n+'.mp3')
            for ln in q.languages.split(','):
                copyfile(fr, join(
                    BASE_DIR,
                    f'erp/media/{t}/|{n}|{ln}|{t}_{c + old + 1}.mp3'))

    if(diff < 0):
        # print('DELETE FILES')
        for sound in list(filter(lambda s:s.startswith('|'), os.listdir(path))):
            for n in range(-diff):
                if str(n + num) in sound:
                    os.remove(path + sound)



def manage_all_sound():
    #TODO: refactor this
    q = load_current_quest()
    languages = q.languages.split(',')
    # current_language = languages[q.selected_language]

    print("DELETE NOT USE LANG SOUND")
    for t in ['action', 'hint','auto']:
        path = join(BASE_DIR, f'erp/media/{t}/')
        all_sounds = os.listdir(path)
        remove_list = os.listdir(path)
        for sound_name in all_sounds:
            if not sound_name.startswith("|"):
                remove_list.remove(sound_name)
                for language in languages:
                    if language in sound_name:
                        remove_list.remove(sound_name)
        for sound_name in remove_list:
            os.remove(path + sound_name)

    print("CREATE NEW LANG SOUND")
    for t in ['action', 'back', 'system']:
        path = join(BASE_DIR, f'erp/media/{t}/')
        sounds = os.listdir(path)
        for sound in sounds:
            print(f'{t}/{sound}')
            if not sound.startswith("|"):
                number, name = sound.split("_", 1)
                fr = join(BASE_DIR, f'erp/media/{t}/', sound)
                if t == 'back' or t == 'system':
                    to = join(BASE_DIR, f'erp/media/{t}/|{number}|ND|{name}')
                    copyfile(fr, to)
                if t == 'action' or t == 'hint':
                    for language in languages:
                        to = join(BASE_DIR, f'erp/media/{t}/|{number}|{language}|{name}')
                        copyfile(fr, to)

    print("CREATE NEW AUTO AND SOUND HINTS")
    for r in q.riddel_set.all():
        add_or_del_sounds(r.auto_hints, 0, r.erp_num, 'auto')
        add_or_del_sounds(r.sound_hints, 0, r.erp_num, 'hint')

#++++++++++++++MAIL++++++++++++++++++++++++++++++++++++
def report(request):
    if request.method == "GET":
        json = {"status": "mail"}
        send_mail()
    return JsonResponse(json)

#-----------------DATA----------------------------------
def data(request):
    if request.method == "GET":
        print("DATA")
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
        for n, rid in zip(range(rn), q.riddel_set.all()):
            json['riddles'][n] = {'strId': rid.erp_name, 'strName': rid.panel_name, 'strStatus':"Not activated", 'number': rid.erp_num, 'sound_buttons': rid.sound_hints, 'video_buttons': rid.video_hints}
        print(json)
    return JsonResponse(json)

def statistic(request, action=''):
    if request.method == "GET":
        if action == 'start':
            s = Statistic(status='start quest')
            s.save()
            json = {"status": "start"}
        if action == 'reset':
            s = Statistic(status='reset quest')
            s.save()
            json = {"status": "reset"}
        if action == 'timeup':
            s = Statistic(status='finish time')
            s.save()
            json = {"status": "time up"}
    return JsonResponse(json)

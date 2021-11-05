from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# class Panel(models.Model):
#     class Meta:
#         verbose_name = "Panel-State"
#     id = models.AutoField(primary_key=True)
#     quest = models.CharField(max_length=30)

#     def __str__(self):
#         return f"CURRENT QUEST: {self.quest}"

class Quest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    main_vol = models.PositiveSmallIntegerField(default=60)
    back_vol = models.PositiveSmallIntegerField(default=60)
    playing_time = models.PositiveSmallIntegerField(default=60)
    start_offset = models.PositiveSmallIntegerField(default=0)

    show_video_hints = models.BooleanField(default=False)
    show_audio_hints = models.BooleanField(default=False)

    show_autohints = models.BooleanField(default=False)
    show_dificult = models.BooleanField(default=False)
    show_languages = models.BooleanField(default=False)
    show_start_offset = models.BooleanField(default=False)

    selected_dificult = models.PositiveSmallIntegerField(default=0)

    selected_language = models.PositiveSmallIntegerField(default=0)
    languages = models.CharField(max_length=50, default='EN')

    def __str__(self):
        return self.name

class Riddel(models.Model):
    id = models.AutoField(primary_key=True)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)

    panel_order = models.PositiveSmallIntegerField(default=0)
    erp_num = models.PositiveSmallIntegerField(default=0)

    erp_name = models.CharField(max_length=22, default='')
    panel_name = models.CharField(max_length=22, default='')

    sound_hints = models.PositiveSmallIntegerField(default=0)
    video_hints = models.PositiveSmallIntegerField(default=0)
    auto_hints = models.PositiveSmallIntegerField(default=0)
    autoi = models.CharField(max_length=20, default='', blank=True)

    def __str__(self):
        return f"{self.quest}: {self.erp_num}-{self.erp_name}"


class Panel(models.Model):
    class Meta:
        verbose_name = "Selected quest"
    id = models.AutoField(primary_key=True)
    quest = models.ForeignKey(Quest, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"CURRENT QUEST: {self.quest}"

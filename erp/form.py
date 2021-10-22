from django import forms
from .models import Configuration


class Config(forms.Form):
    class Meta:
        model = Configuration

    name = forms.CharField(max_length=30, help_text="Test")
    ek = forms.IntegerField()



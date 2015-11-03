__author__ = 'RongShun'

from django import forms
from django.db import models
from django.forms import ModelForm
from lib.common.commands.adb import Adb
from lib.common.constant import SCRIPTED_PROFILE_INTERACTION, RANDOM_INTERACTION
from lib.core.managers.session import get_current_device_serial

adb= Adb()
class ConfigForm(forms.Form):
    """
    django profile1 form for displaying profile options.
    for more information visit https://docs.djangoproject.com/en/1.7/ref/forms/fields/
    """
    enable_profile = forms.BooleanField()
    choices = (
        (SCRIPTED_PROFILE_INTERACTION, "run profile simulation script"),
        (RANDOM_INTERACTION, "random simulation")
    )
    simulation_option = forms.ChoiceField(choices)

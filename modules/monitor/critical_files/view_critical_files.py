__author__ = 'RongShun'

from django import forms
from django.db import models
from django.forms import ModelForm
from lib.common.commands.adb import Adb
from lib.core.managers.session import get_current_device_serial

adb = Adb()
class ConfigForm(forms.Form):
    #get init files from device
    get_init_files_command = "ls /*init*"
    result = adb.shell(get_init_files_command, root=True, device_serial=get_current_device_serial())
    init_files = result.std_output

    init_files_choice = []

    for init_file in init_files:
        choice = (init_file, init_file)
        init_files_choice.append(choice)

    system_initilize_files = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=init_files_choice, required=False)
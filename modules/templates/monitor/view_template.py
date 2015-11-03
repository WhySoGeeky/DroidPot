__author__ = 'RongShun'

from django import forms
from django.db import models
from django.forms import ModelForm
from lib.common.commands.adb import Adb
from lib.core.managers.session import get_current_device_serial

adb = Adb()
class ConfigForm(forms.Form):
    """
    This class handles the creation of django form on configuration interface.
    For more information on django form, visit https://docs.djangoproject.com/en/1.7/ref/forms/fields/
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    NOTE: get_current_device_serial() method is useful to get the device's serial number that you are interested in.
    You might need it to extract information from the particular device for form manipulation
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    """

    #EXAMPLE FORM
    get_init_files_command = "ls"
    result = adb.shell(get_init_files_command, root=True, device_serial=get_current_device_serial())
    files = result.std_output

    files_choice = []
    for init_file in files:
        choice = (init_file, init_file)
        files_choice.append(choice)

    system_initilize_files = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=files_choice, required=False)
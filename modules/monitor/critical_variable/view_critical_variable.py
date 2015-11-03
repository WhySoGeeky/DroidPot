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

    critical_variables = (
        ("LD_PRELOAD", "$LD_PRELOAD"),
        ("PATH", "$PATH")
    )
    system_variables = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=critical_variables, required=False)
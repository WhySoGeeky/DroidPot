from django.db import models
from django.forms import ModelForm

# Create your models here.

class Sandbox_Session(models.Model):
    CONFIGURING = "CFG"
    INITILIZING = "INI"
    ANALYSING = "ANA"
    FINISHED = "FIN"
    CANCELLED = "CAN"
    HOLD = "HOL"

    STATUS_CHOICES = (
        (CONFIGURING, 'Configuring'),
        (INITILIZING, 'Initilizing'),
        (ANALYSING, 'Analysing'),
        (FINISHED, "Finished"),
    )


    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=CONFIGURING)
    start_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    configuration = models.TextField()
    apk_paths = models.TextField()
    device_backup_path = models.TextField()
    analysis_duration = models.PositiveIntegerField(help_text="(In Minutes)", default=30)
    device_serial = models.TextField()
    status_log = models.TextField()
    end_time = models.DateTimeField(null=True)
    is_stopping = models.BooleanField(default=False)


class Session_result(models.Model):
    id = models.AutoField(primary_key=True)

    package_name = models.TextField(blank=True)
    start_time = models.TextField(blank=True)
    end_time = models.TextField(blank=True)
    device_name = models.TextField(blank=True)
    sample_size = models.TextField(blank=True)
    device_serial = models.TextField(blank=True)
    md5 = models.TextField(blank=True)
    sha1 = models.TextField(blank=True)
    sha256 = models.TextField(blank=True)

    session = models.OneToOneField(Sandbox_Session)

class ResultsForm(ModelForm):
    class Meta:
        model = Session_result
        fields = ['session', 'start_time', 'end_time', 'package_name', 'md5']

class AnalysisDurationForm(ModelForm):
    class Meta:
        model = Sandbox_Session
        fields = ['analysis_duration']

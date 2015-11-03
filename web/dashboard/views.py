from django.shortcuts import render, render_to_response, redirect, HttpResponse
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
#import modules.processing.general_information.general_information as gi_obj

import os, sys, ast, json, time, hashlib, json
from json2html import *
from models import Sandbox_Session, AnalysisDurationForm, Session_result, ResultsForm
# Create your views here.

import logging, datetime
log = logging.getLogger(__name__)

DIR_PATH = os.path.join(os.getcwd())
sys.path.append(DIR_PATH)

from lib.core.managers.session import SessionManager, Session
from lib.core.managers.plugin import MonitorsManager, ProfilesManager, ProcessingManager
from lib.common.commands.adb import Adb
from lib.core.partitions import Partition
from lib.common.constant import APK_BASE_DIR

monitorsManager = MonitorsManager()
profileManager = ProfilesManager()
sessionManager = SessionManager()
partition = Partition()
adb = Adb()




def index(request):
    '''
    Dashboard controller
    :param request:
    :return:
    '''
    if request.method == 'GET':
        #check for existing incomplete session
        session = Sandbox_Session()
        try:
            current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
            create_new_session = False

        except Sandbox_Session.DoesNotExist:
            session.save()
            current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
            create_new_session = True


        session_config = None
        try:
            session_config = ast.literal_eval(current_session.configuration)
            #retrieve any existing configurations in database
        except SyntaxError:
            pass

        devices = adb.devices()
        if len(devices) == 1:
            for device, status in devices.iteritems():
                current_session.device_serial = device
                current_session.save()
                current_session = Sandbox_Session.objects.get(id=current_session.id)

        profileModules = profileManager.modules_info()
        monitorModules = monitorsManager.modules_info()
        monitor_total = monitorsManager.count_modules()

        sessions = Sandbox_Session.objects.all()
        params = {
            "selected_device":current_session.device_serial,
            "profileModules":profileModules,
            "monitorModules":monitorModules,
            "create_new_session":create_new_session,
            "current_session":current_session,
            "module_total":monitor_total,
            "session_config":session_config,
            "sessions":sessions,
            "devices":devices,
        }
        return render_to_response("dashboard/index.html",params ,context_instance=RequestContext(request))

def check_time(request, id):
    """
    ajax controller for dashboard to check session end time. if overdue, terminate session and end analysis
    :param request:
    :param id:
    :return:
    """
    current_session = Sandbox_Session.objects.get(id=id)
    time_now = datetime.datetime.now().replace(tzinfo=None)

    end_time = current_session.end_time
    is_stopping = current_session.is_stopping

    #print time_now
    #print end_time
    response_data = {}
    if time_now > end_time:
        #print "\n\n\ntime now > endtime\n\n"
        response_data['shouldEnd'] = True
        response_data['is_stopping'] = is_stopping
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        #print "\n\n\ntime now < endtime\n\n"
        response_data['shouldEnd'] = False
        response_data['is_stopping'] = is_stopping
        return HttpResponse(json.dumps(response_data), content_type="application/json")

def progress(request, id):
    '''
    controller for session progress
    :param request:
    :param id:
    :return:
    '''
    #current_session = Sandbox_Session.objects.get(id=id)

    isRestoring = False
    try:
        session = Session(id)
        if os.path.exists(os.path.join(session.logs_dir, "end_status.log")):
            #is recovery process
            status_log = open(os.path.join(session.logs_dir, "end_status.log"), "r")
            isRestoring = True
        else:
            status_log = open(os.path.join(session.logs_dir, "status.log"), "r")

        lines = status_log.readlines()
        status_log.close()
        progress = lines[len(lines)-1]
        progress = progress.split(" - ")[1]
        return render_to_response("dashboard/progress.html", {"progress":progress, "isRestoring":isRestoring}, context_instance=RequestContext(request))
    except Exception as io:
        return render_to_response("dashboard/progress.html", {"progress":"", "isRestoring":isRestoring}, context_instance=RequestContext(request))

def select_device(request, device, id):
    '''
    Controller for selecting devices
    :param request:
    :param device:
    :param id:
    :return:
    '''
    devices = adb.devices()

    for real_device, status in devices.iteritems():
        if real_device == device:
            current_session = Sandbox_Session.objects.get(id=id)
            current_session.device_serial = real_device
            current_session.save()

            return redirect("/")

def upload_sample(request, id):
    """
    handler for apk uploading
    :param request:
    :param id:
    :return:
    """

    profileModules = profileManager.modules_info()
    monitorModules = monitorsManager.modules_info()
    current_session = Sandbox_Session.objects.get(id=id)
    devices = adb.devices()
    params = {
        "profileModules":profileModules,
        "monitorModules":monitorModules,
        "current_session":current_session,
        "devices":devices,
    }
    if request.method == "GET":
        return render_to_response("dashboard/upload.html", params, context_instance=RequestContext(request))

    if request.method == "POST":
        log.debug(request.FILES.getlist('upload'))

        is_uploaded = handle_upload_file(request.FILES.getlist('upload'), id)

        params["upload_result"] = is_uploaded

        return render_to_response("dashboard/upload.html", params, context_instance=RequestContext(request))


def analysis_duration(request, id):
    """
    handler to set duration for analysis. Duration will be stored in database in minutes
    :param request:
    :return:
    """

    profileModules = profileManager.modules_info()
    monitorModules = monitorsManager.modules_info()
    current_session = Sandbox_Session.objects.get(id=id)
    devices = adb.devices()

    analysisDurationForm  = AnalysisDurationForm(instance=current_session)
    params = {
        "analysisDurationForm": analysisDurationForm,
        "profileModules":profileModules,
        "monitorModules":monitorModules,
        "current_session":current_session,
        "devices":devices,
    }
    if request.method == "GET":
        return render_to_response("dashboard/duration.html", params, context_instance=RequestContext(request))

    if request.method == "POST":
        analysisDurationForm  = AnalysisDurationForm(request.POST, instance=current_session)
        duration_result = analysisDurationForm.save()

        this_session = Sandbox_Session.objects.get(id=id)

        hold_sessions = Sandbox_Session.objects.filter(status=Sandbox_Session.HOLD)
        for hold_session in hold_sessions:
            hold_session.analysis_duration = this_session.analysis_duration
            hold_session.save()

        params["duration_result"] = duration_result
        params["analysisDurationForm"] = analysisDurationForm

        return render_to_response("dashboard/duration.html", params, context_instance=RequestContext(request))



def handle_upload_file(files, id):
    """
    Save uploaded apk to droidpot apk folder and save apk paths to session database
    :param files: uploaded file[s] in POST form
    :param id: session id
    :return: bool
    """
    current_session = Sandbox_Session.objects.get(id=id)

    total_samples = len(files)
    if total_samples > 1:
        #create holding sessions
        for i in range(0, total_samples-1, 1):
            session = Sandbox_Session()
            session.status = Sandbox_Session.HOLD
            session.configuration = current_session.configuration
            session.analysis_duration = current_session.analysis_duration
            session.device_serial = current_session.device_serial
            session.save()


    count = 0
    first_id = current_session.id
    for file in files:
        sample_path = {}
        file_name = file.__str__()

        temp_file_path = os.path.join(APK_BASE_DIR, file_name)

        with open(temp_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        file_md5 = hashlib.md5(open(temp_file_path).read()).hexdigest()

        new_file_name = file_md5 + "_" + file_name
        new_file_path = os.path.join(APK_BASE_DIR, new_file_name)
        sample_path[new_file_name] = new_file_path


        if not os.path.exists(new_file_path):
            os.rename(temp_file_path, new_file_path)
            log.info("New sample uploaded")

        else:
            log.info("Identical sample found.")
            os.remove(temp_file_path)

        each_session = Sandbox_Session.objects.get(id=first_id+count)
        each_session.apk_paths = sample_path
        each_session.save()
        count +=1

    return True


def new_session(request):
    '''
    Controller for new session creation
    :param request:
    :return:
    '''
    previous_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
    previous_session.status = Sandbox_Session.CANCELLED
    previous_session.save()

    hold_sessions = Sandbox_Session.objects.filter(status=Sandbox_Session.HOLD)

    for hold_session in hold_sessions:
        hold_session.status = Sandbox_Session.CANCELLED
        hold_session.save()

    return redirect('/')

def end_session(request, session_id):
    """
    Ends the analysis session
    Restore device to original state
    :param request:
    :param session_id:
    :return:
    """
    try:
        session = Sandbox_Session.objects.get(id=session_id)
        session.is_stopping = True
        session.save()
        try:
            modules_config = ast.literal_eval(session.configuration)
        except SyntaxError:
            modules_config = {}

        is_ended = sessionManager.end(session_id=session_id, device_backup_path=session.device_backup_path, modules_config=modules_config, device_serial=session.device_serial)
        if is_ended:
            session.status = Sandbox_Session.FINISHED
            session.save()

        processing(request, session_id)

        #handling multiple samples
        hold_sessions = Sandbox_Session.objects.filter(status=Sandbox_Session.HOLD)
        for hold_session in hold_sessions:
            print "running next sample"
            initialize(request, hold_session.id)
            break

    except Exception as e:
        raise e

    return redirect("index")

def processing(request, id):
    """
    call processing modules to process raw data gathered from session
    :param request:
    :param id:
    :return:
    """
    SESSION_ID = "id"
    START_TIME = "start_time"
    END_TIME = "end_time"
    SAMPLE_HASH = "sample_hash"
    SAMPLE_SIZE = "sample_size"
    PACKAGE_NAME = "package_name"
    DEVICE_NAME = "device_name"
    DEVICE_SERIAL = "device_serial"

    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"

    processingModules = ProcessingManager()
    results = processingModules.run(id)

    for module_name, result_json in results.iteritems():
        sessionManager.save_result(id, module_name, result_json, ext=".json")


    general_info = processingModules.general_information(id)
    session_result = Session_result()
    session_result.session = Sandbox_Session(id)

    session_result.device_name = general_info[DEVICE_NAME]
    session_result.md5 = general_info[SAMPLE_HASH][MD5]
    session_result.sha1 = general_info[SAMPLE_HASH][SHA1]
    session_result.sha256 = general_info[SAMPLE_HASH][SHA256]
    session_result.end_time = general_info[END_TIME]
    session_result.sample_size = general_info[SAMPLE_SIZE]
    session_result.device_serial = general_info[DEVICE_SERIAL]
    session_result.start_time = general_info[START_TIME]
    session_result.package_name = general_info[PACKAGE_NAME]
    try:
        session_result.save()
    except Exception as e:
        pass


    return HttpResponse(json.dumps(""), content_type="application/json")


def report(request, session_id):
    profileModules = profileManager.modules_info()
    monitorModules = monitorsManager.modules_info()

    current_session = Sandbox_Session.objects.get(id=session_id)

    reports = Session_result.objects.all()


    devices = adb.devices()
    params = {
        "profileModules":profileModules,
        "monitorModules":monitorModules,
        "current_session":current_session,
        "devices":devices,
        "reports":reports,
    }

    if request.method == "GET":
        return render_to_response("dashboard/report.html", params, context_instance=RequestContext(request))

    if request.method == "POST":
        #go into details of report
        pass

def report_details(request, session_id):
    profileModules = profileManager.modules_info()
    monitorModules = monitorsManager.modules_info()
    current_session = Sandbox_Session.objects.get(id=session_id)
    devices = adb.devices()

    detailed_reports = sessionManager.get_results(session_id)

    detailed = {}
    for report_name, report_json in detailed_reports.iteritems():
        try:
            detailed[report_name] = json2html.convert(json=report_json, table_attributes="class=\"table table-border table-hover\"")
        except Exception as e:
            pass

    params = {
        "profileModules":profileModules,
        "monitorModules":monitorModules,
        "current_session":current_session,
        "devices":devices,
        "detailed":detailed,
    }


    return render_to_response("dashboard/detailed_report.html", params, context_instance=RequestContext(request))

def initialize(request, id):
    """
    Initilize the device for malware analysis.
    :param request:
    :param id: current session id
    :return: index page if successful. summary page if error occurred
    """


    current_session = Sandbox_Session.objects.get(id=id)
    current_session.status = Sandbox_Session.ANALYSING
    device_serial = current_session.device_serial
    current_session.save()

    try:
        modules_config = ast.literal_eval(current_session.configuration)
    except SyntaxError:
        modules_config = {}

    try:
        apk_paths = ast.literal_eval(current_session.apk_paths)
    except SyntaxError:
        apk_paths = {}

    device_backup_path, status_log, end_time = sessionManager.start(session_id=id, modules_config=modules_config, apk_paths=apk_paths, duration=current_session.analysis_duration, device_serial=device_serial)

    if device_backup_path and status_log and end_time:
        log.info("Analysis initialize successfully")
        current_session.status = Sandbox_Session.ANALYSING
        current_session.device_backup_path = device_backup_path
        current_session.status_log = status_log
        current_session.end_time = end_time
        current_session.save()
        #return redirect('index')
    else:
        log.critical("Analysis initialization error")
        #return redirect('summary', id)

    return redirect('index')


def profiles(request):
    '''
    Controller for profile module page
    :param request:
    :return:
    '''
    request_path = request.path
    request_path = request_path.split('/')
    module_name = request_path[len(request_path) - 1]

    current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
    profileModules =  profileManager.modules_info()


        #profileManager.configForms(current_session.device_serial, module_name)
    if request.method == 'GET':
        apply =  request.GET.get("apply")

        current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
        module_params = {}
        try:
            configuration = ast.literal_eval(current_session.configuration)
            #retrieve any existing configurations in database
            for module, params in configuration.iteritems():
                if module == module_name:
                    module_params = params
        except SyntaxError:
            pass

        #retrieve form object form module
        module_form = profileManager.configForms(current_session.device_serial, module_name)
        module_info = object
        for name, pluginInfo in profileModules.iteritems():

            if name == module_name:
                module_info = pluginInfo

        profileModules = profileManager.configForms(current_session.device_serial)
        monitorModules = monitorsManager.modules_info()
        params = {
            "isProfile":True,
            "module_form":module_form,
            "monitorModules":monitorModules,
            "profileModules":profileModules,
            "module_info":module_info,
            "apply":apply,
            "current_session":current_session,
        }
        return render_to_response("dashboard/profiling.html", params, context_instance=RequestContext(request))


    if request.method == "POST":
        config = {module_name:{}}

        params = request.POST
        for key in params.iterkeys():
            value = request.POST.getlist(key)
            if key == "csrfmiddlewaretoken" or key == "action":
                pass
            else:
                #extract the only element in value list with 1 element
                if len(value) == 1:
                    config[module_name][key] = value[0]
                else:
                    config[module_name][key] = value

        config[module_name]["module_type"] = "profile"

        current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
        if current_session.configuration:
            configuration = ast.literal_eval(current_session.configuration)
            for key,value in config.iteritems():
                configuration[key] = value
                current_session.configuration = configuration
        else:
            current_session.configuration = config

        current_session.save()

        hold_sessions = Sandbox_Session.objects.filter(status=Sandbox_Session.HOLD)
        for hold_session in hold_sessions:
            hold_session.configuration = current_session.configuration
            hold_session.save()

        return redirect('/profiles/'+module_name+"?apply=True")



def monitoring(request):
    '''
    Controller for monitoring module page
    :param request:
    :return:
    '''
    monitorsManager = MonitorsManager()
    request_path = request.path
    request_path = request_path.split('/')
    module_name = request_path[len(request_path) - 1]

    current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
    module_form = monitorsManager.configForms(current_session.device_serial, module_name)

    module_info = monitorsManager.modules_info(module_name=module_name)

    if request.method == 'GET':
        apply =  request.GET.get("apply")

        current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
        module_params = {}
        try:
            configuration = ast.literal_eval(current_session.configuration)
            #retrieve any existing configurations in database
            for module, params in configuration.iteritems():
                if module == module_name:
                    module_params = params
        except SyntaxError:
            pass
        '''
        #retrieve form object form module
        module_form = object
        module_info = object
        for pluginInfo, form in monitorModules.iteritems():
            if pluginInfo.name == module_name:
                module_form = form(module_params)
                module_info = pluginInfo
        '''

        profileModules = profileManager.modules_info()
        monitorModules = monitorsManager.modules_info()
        params = {
            "isMonitoring":True,
            "module_form":module_form,
            "profileModules":profileModules,
            "monitorModules":monitorModules,
            "module_info":module_info,
            "apply":apply,
            "current_session":current_session,
        }
        return render_to_response("dashboard/monitoring.html", params, context_instance=RequestContext(request))

    if request.method == "POST":
        config = {module_name:{}}

        params = request.POST
        for key in params.iterkeys():
            value = request.POST.getlist(key)
            if key == "csrfmiddlewaretoken" or key == "action":
                pass
            else:
                #extract the only element in value list with 1 element
                if len(value) == 1:
                    config[module_name][key] = value[0]
                else:
                    config[module_name][key] = value

        config[module_name]["module_type"] = "monitor"

        current_session = Sandbox_Session.objects.get(status=Sandbox_Session.CONFIGURING)
        if current_session.configuration:
            configuration = ast.literal_eval(current_session.configuration)
            for key,value in config.iteritems():
                configuration[key] = value
                current_session.configuration = configuration
        else:
            current_session.configuration = config

        current_session.save()

        hold_sessions = Sandbox_Session.objects.filter(status=Sandbox_Session.HOLD)

        for hold_session in hold_sessions:
            hold_session.configuration = current_session.configuration
            hold_session.save()

        return redirect('/monitoring/'+module_name+"?apply=True")


def summary(request, id):
    '''
    Controller for displaying configuration summary before analysis
    :param request:
    :param id:
    :return:
    '''
    current_session = Sandbox_Session.objects.get(id=id)
    if current_session.status == Sandbox_Session.INITILIZING:
        init_error = True
        current_session.status = Sandbox_Session.CONFIGURING
        current_session.save()
    else:
        init_error = False
    try:
        configuration = ast.literal_eval(current_session.configuration)
    except SyntaxError:
        configuration = {}

    params = {
        "configuration":configuration,
        "current_session":current_session,
        "summary":True,
        "init_error":init_error,
    }

    return render_to_response("analysis/summary.html",params ,context_instance=RequestContext(request))

def init_loading(request, id):
    '''
    Controller for showing initilize status page
    :param request:
    :param id:
    :return:
    '''
    current_session = Sandbox_Session.objects.get(id=id)

    params = {
        "current_session":current_session,

    }

    return render_to_response("analysis/loading.html", params, context_instance=RequestContext(request))



def copy_config(request, from_id, to_id):
    '''
    Controller for copying configuration from previous session
    :param request:
    :param from_id:
    :param to_id:
    :return:
    '''
    to_session = Sandbox_Session.objects.get(id=to_id)
    from_session = Sandbox_Session.objects.get(id=from_id)

    to_session.configuration = from_session.configuration
    #to_session.apk_paths = from_session.apk_paths
    to_session.device_serial = from_session.device_serial
    to_session.analysis_duration = from_session.analysis_duration
    to_session.save()

    hold_sessions = Sandbox_Session.objects.filter(status=Sandbox_Session.HOLD)

    for hold_session in hold_sessions:
        hold_session.configuration = from_session.configuration
        hold_session.device_serial = from_session.device_serial
        hold_session.analysis_duration = from_session.analysis_duration
        hold_session.save()

    return redirect('index')



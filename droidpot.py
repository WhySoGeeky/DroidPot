__author__ = 'RongShun'
import argparse, sys, time, logging, subprocess, os, shutil, fileinput
from lib.common.logo import logo
from lib.core.startup import check_root, init_logging, check_modules, check_device_compatibility, check_ini_files
from lib.common.exceptions import DroidCriticalError, InitilizeError
from lib.common.constant import PROFILE_MODULE_DIR, MONITOR_MODULE_DIR, BASE_PATH, REPORTING_MODULE_DIR, PROCESSING_MODULE_DIR

log = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description="Open source android malware analysis sandbox")

def create_profile_module(module_name):
    """
    create new profile module directory from template
    :param module_name: module's name
    :return:
    """
    module_name.replace(" ", "")
    new_profile_path = os.path.join(PROFILE_MODULE_DIR, module_name)

    profile_template_dir = os.path.join(BASE_PATH, "modules", "templates", "profile")

    try:
        shutil.copytree(profile_template_dir, new_profile_path)
    except shutil.Error as e:
        log.exception("Profile directory not created. Error: %e" %e)
        exit(1)

    files = ["template.plugin", "template.py", "view_template.py"]
    for file_name in files:
        file_path = os.path.join(new_profile_path, file_name)

        new_file_name = file_name.replace("template",module_name)
        new_file_path = os.path.join(new_profile_path, new_file_name)

        file = open(file_path, 'r')
        filedata = file.read()
        file.close()
        newdata = filedata.replace("template", module_name)
        f = open(new_file_path, 'w')
        f.write(newdata)
        f.close()

        os.remove(file_path)

def create_processing_module(module_name):
    """
    create new processing module directory from template
    :param module_name: moduel's name
    :return:
    """
    module_name.replace(" ", "")
    new_processing_path = os.path.join(PROCESSING_MODULE_DIR, module_name)
    processing_template_dir = os.path.join(BASE_PATH, "modules", "templates", "processing")

    try:
        shutil.copytree(processing_template_dir, new_processing_path)
    except shutil.Error as e:
        log.exception("Profile directory not created. Error: %e" %e)
        exit(1)

    files = ["template.plugin", "template.py"]
    for file_name in files:
        file_path = os.path.join(new_processing_path, file_name)

        new_file_name = file_name.replace("template",module_name)
        new_file_path = os.path.join(new_processing_path, new_file_name)

        file = open(file_path, 'r')
        filedata = file.read()
        file.close()
        newdata = filedata.replace("template", module_name)
        f = open(new_file_path, 'w')
        f.write(newdata)
        f.close()
        os.remove(file_path)


def create_reporting_module(module_name):
    """
    create new reporting module directory from template
    :param module_name: moduele's name
    :return:
    """
    module_name.replace(" ", "")
    new_reporting_path = os.path.join(REPORTING_MODULE_DIR, module_name)
    reporting_template_dir = os.path.join(BASE_PATH, "modules", "templates", "processing")

    try:
        shutil.copytree(reporting_template_dir, new_reporting_path)
    except shutil.Error as e:
        log.exception("Profile directory not created. Error: %e" %e)
        exit(1)

    files = ["template.plugin", "template.py"]
    for file_name in files:
        file_path = os.path.join(new_reporting_path, file_name)

        new_file_name = file_name.replace("template",module_name)
        new_file_path = os.path.join(new_reporting_path, new_file_name)

        file = open(file_path, 'r')
        filedata = file.read()
        file.close()
        newdata = filedata.replace("template", module_name)
        f = open(new_file_path, 'w')
        f.write(newdata)
        f.close()
        os.remove(file_path)



def create_monitor_module(module_name):
    """
    create new monitor module directory from template
    :param module_name: module's name
    :return:
    """
    module_name.replace(" ", "")
    new_monitor_path = os.path.join(MONITOR_MODULE_DIR, module_name)

    monitor_template_dir = os.path.join(BASE_PATH, "modules", "templates", "monitor")

    try:
        shutil.copytree(monitor_template_dir, new_monitor_path)
    except shutil.Error as e:
        log.exception("Profile directory not created. Error: %e" %e)
        exit(1)

    files = ["template.plugin", "template.py", "view_template.py"]
    for file_name in files:
        file_path = os.path.join(new_monitor_path, file_name)

        new_file_name = file_name.replace("template",module_name)
        new_file_path = os.path.join(new_monitor_path, new_file_name)

        file = open(file_path, 'r')
        filedata = file.read()
        file.close()
        newdata = filedata.replace("template", module_name)
        f = open(new_file_path, 'w')
        f.write(newdata)
        f.close()

        os.remove(file_path)





def init_droidpot(debug=False, quiet=False, new_module=[]):
    """
    Initilize droidpot. Checks environment, set console log level,
    initilize managers and start django web interface
    :param debug: debug mode
    :param quiet: quiet mode
    :return: nil
    """
    try:
        if new_module:
            #adding new module
            MODULE_TYPE = 0
            MODULE_NAME = 1
            if new_module[MODULE_TYPE] ==  "monitor":
                print "Creating monitor module %s ..."%new_module[MODULE_NAME]
                create_monitor_module(new_module[MODULE_NAME])
                exit(0)
            elif new_module[MODULE_TYPE] == "profile":
                print "Creating profile module %s ..."%new_module[MODULE_NAME]
                create_profile_module(new_module[MODULE_NAME])
                exit(0)
            elif new_module[MODULE_TYPE] == "processing":
                print "Creating processing module %s ..."%new_module[MODULE_NAME]
                create_processing_module(new_module[MODULE_NAME])
                exit(0)
            else:
                print "error. exiting..."
                exit(1)
            '''
            elif new_module[MODULE_TYPE] == "reporting":
                print "Creating reporting module %s ..."%new_module[MODULE_NAME]
                create_reporting_module(new_module[MODULE_NAME])
                exit(0)
            '''




        logo()
        init_logging()
        check_ini_files()
        #check_device_compatibility()
        check_root()
        check_modules()
        log.info("Modules loaded successfully")
        if debug:
            log.setLevel(logging.DEBUG)
        if quiet:
            log.setLevel(logging.WARN)

        log.info("Starting Django web interface")
        subprocess.call(["python", "web/manage.py", "migrate","--verbosity", "0"])
        subprocess.call(["python", "web/manage.py", "runserver"])

    except InitilizeError as ie:

        exit(1)
    except KeyboardInterrupt:
        exit(0)




    #modules = {"Syscall Monitor": {"param1":"value1"}}
    #sm.start_analysis(modules)
    #sm.create_session()

def droidpot():
    parser.add_argument("-d","--debug", help="Display debug messages", action='store_true', required=False)
    parser.add_argument("-q","--quiet", help="Display only error messages", action='store_true', required=False)
    parser.add_argument("-a","--add", help="Add new module < monitor | profile | processing> <module name>", nargs=2, required=False)
    args = parser.parse_args()


    try:
        init_droidpot(debug=args.debug, quiet=args.quiet, new_module=args.add)
    except DroidCriticalError as e:
        message = "{0}: {1}".format(e.__class__.__name__, e)
        sys.stderr.write("{0}\n".format(message))



if __name__ == "__main__":
    droidpot()

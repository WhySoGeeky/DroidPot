from os.path import abspath, dirname, normpath, join

#get absolute base path of honeypot

_current_dir = abspath(dirname(__file__))
BASE_PATH = normpath(join(_current_dir, "..", ".."))


SUCCESSFUL = True
UNSUCCESSFUL = False

#plugin directory
MONITOR_MODULE_DIR = join(BASE_PATH, "modules", "monitor")
PROFILE_MODULE_DIR = join(BASE_PATH, "modules", "profiles")
PROCESSING_MODULE_DIR = join(BASE_PATH, "modules", "processing")
PROCESSING_MODULE_DIR = join(BASE_PATH, "modules", "processing")
REPORTING_MODULE_DIR = join(BASE_PATH, "modules", "reporting")

#apk directory
APK_BASE_DIR = join(BASE_PATH, "samples")

#profile simulation type
SCRIPTED_PROFILE_INTERACTION = "monkey"
RANDOM_INTERACTION = "random"


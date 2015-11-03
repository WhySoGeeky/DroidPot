.. DroidPot documentation master file, created by
   sphinx-quickstart on Fri Oct 30 11:19:59 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DroidPot's documentation!
====================================
DroidPot is a highly customizable android malware analysis framework that is written with various libraries,frameworks and tools.
It includes Django framework 1.8.5, python 2.7, json2html, adb, fastboot, mkbootimg and twrp.

Droidpot allows developer to create modules monitoring, device profiling, automated interactions and processing raw data from monitoring

Details regarding library requirements can be obtain from 'requirements.txt'

====================================
Setup
====================================
On ubuntu machine

#. ``sudo apt-get install pip android-tools-adb android-tools-fastboot``
#. Navigate to droidpot root folder in terminal, where ``requirements.txt`` is found.
#. Install all prerequisite libraries and modules by typing ``pip install -r requirements.txt`` in terminal. ``sudo`` if required
#. Set your device details in ``devices.ini``, located in root directory of droidpot

===================================
How to start DroidPot
===================================
**Steps:**

#. Navigate to DroidPot root directorey
#. run droidpot.py by typing ``python droidpot.py`` in terminal
#. Visit the dashboard via any browser with the url ``localhost:8000``

==================================
How to write modules
==================================
Droidpot allows analyst to create modules to suit their own analysis needs.

**Types of modules:**

#. monitor: monitoring module to perform device monitoring
#. processing: process the raw data obtained from monitor module after each session
#. profile: device profiling (i.e: installation of apps, preload contact database, preload accounts) and simulate device interaction

To create a new module:
``python droidpot.py --add <profile | processing | monitor> <profile name>``

template for the module will be created automatically inside modules/ directory

=================================
Directories
=================================
Droidpot is organised in the following directories

===================== ===============================
directory                 Description
===================== ===============================
lib                     Contains all important libraries of droidpot framework
modules                 Contains profile, monitor and processing modules
samples					Contains all the analysis samples
sessions				Contains all the analysis sessions
tests					Contains random tests and unittest
tools 					Contains tools made by other developers for droidpot to work
web 					Contains Django interface
devices					Contains important tools, backups for android devices
==================== ===============================

===============================
Developer's Guide
===============================

Modules:

.. toctree::
	:maxdepth: 2

	monitor
	profiles
	processing




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Contents:

.. toctree::
   :maxdepth: 2

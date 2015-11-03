__author__ = 'RongShun'

from subprocess import check_output, Popen, CalledProcessError
import subprocess

import logging
#logging.basicConfig(level=logging.DEBUG)
logs = logging.getLogger("Command")

class result(object):
    def __init__(self):
        self.std_output = []
        self.std_error = ""
        self.isSuccess = True

class Command(object):
    """
    Base class for Commands
    """
    def __init__(self):
        self.COMMAND = ""
        self.DEVICE = ""
        self.OPTION = []
        self.PARAMETERS = []
        self.RESULT = result()

    def setOption(self, options):
        if not str(options):
            raise ValueError

        options_list = []
        for option in options.split(" "):
            options_list.append(option)

        self.OPTION = list(options_list)
        self.PARAMETERS = []
        self.RESULT = result()

    def setCommand(self, command):
        if not str(command):
            raise ValueError

        self.COMMAND = command
        self.OPTION = []
        self.PARAMETERS = []
        self.RESULT = result()

    def setDevice(self, device_serial):
        self.DEVICE = device_serial


    def setParameters(self, parameters):
        if not str(parameters):
            raise ValueError

        parameters_list = []
        for parameter in parameters.split(" "):
            parameters_list.append(parameter)

        self.PARAMETERS = list(parameters_list)
        self.RESULT = result()

    def execute(self, command="", option="", parameter="", device=""):
        """
        Execute command and return result if required. Output is returned by default
        :param command: command
        :param option: options of command
        :param parameter: parameters of options
        :param wait_complete: wait for the command to complete before executing next command
        :return: Result object
        """

        if command:
            self.COMMAND = command
            self.OPTION = option

            if parameter:
                self.PARAMETERS = parameter

            if device:
                self.DEVICE = device

        if not self.COMMAND:
            raise AssertionError

        input = [self.COMMAND,]
        if self.DEVICE:
            input.extend(["-s", self.DEVICE])

        input.extend(self.OPTION)
        input.extend(self.PARAMETERS)

        logs.debug("Executing command: %s" % ' '.join(input))

        proc = subprocess.Popen(input, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.communicate()
        try:
            proc.terminate()
        except OSError as e:
            pass

        std_output = output[0]
        std_error = output[1]

        if not std_error:
            logs.debug("stdout: " + std_output)
            lines = std_output.replace("\r","").split("\n")
            filtered_lines = []
            for line in lines:
                if line:
                    filtered_lines.append(line)

            self.RESULT.std_output = filtered_lines
            self.RESULT.isSuccess = True
        else:
            logs.debug("stderr: " + std_error)
            self.RESULT.std_error = std_error
            self.RESULT.isSuccess = False

        return self.RESULT



        '''
        if wait_complete == False:
            #don't bother about output
            try:
                #logs.debug("Command running without output required")
                subprocess.call(" ".join(input))
                self.RESULT.isSuccess = True
            except ValueError as e:

                e.message = "cannot execute command"
                self.RESULT.isSuccess = False

            return self.RESULT
        else:
            try:
                #logs.debug("Command running with output required")
                self.RESULT.std_output = check_output(input, stderr=subprocess.STDOUT).replace("\r", "").split("\n")
                self.RESULT.isSuccess = True

            except CalledProcessError as c:
                self.RESULT.std_error = c.output
                self.RESULT.isSuccess = False


            return self.RESULT
        '''


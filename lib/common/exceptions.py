__author__ = 'RongShun'

class CommandCriticalError(Exception):
    """
    Unexpected error in command execution
    """
    pass

class NotRootUserError(Exception):
    pass

class DroidCriticalError(Exception):
    pass

class InitilizeError(Exception):
    pass

class SessionDirError(Exception):
    pass

class BackupError(Exception):
    pass

class PartitionError(Exception):
    pass
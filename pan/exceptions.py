class APICallError(Exception):
    """Bad API Call"""
    def __init__(self, errors):
        self.errors = errors
    def __str__(self):
        return repr(self.errors)

class UnknownAPICall(APICallError):
    """Unknown API Call"""

class InitError(APICallError):
    """Error in initialization"""

class ObjectTypeError(APICallError):
    """Incorrect Object Type"""

class IOError(APICallError):
    """Incorrect Object Type"""

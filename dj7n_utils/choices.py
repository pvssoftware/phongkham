from enum import Enum

class Priority(str, Enum):
    """
    the way to get value: Priority.LOCAL.value
    """
    LOCAL = "local"
    TESTING = "testing"
    PROD = "prod"
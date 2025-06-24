from threading import Lock
from functools import wraps

def singleton(cls):
    _instances = {}
    _lock = Lock()

    @wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal _instances
        with _lock:
            if cls not in _instances:
                _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return wrapper

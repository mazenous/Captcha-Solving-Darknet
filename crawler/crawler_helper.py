from functools import wraps


def logger(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f"Calling {f.__name__}")
        return f(*args, **kwargs)

    return wrapper

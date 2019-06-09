import json


def get_params(argv):
    params = {}
    key = ""
    for arg in argv:
        if "=" in arg:
            key, value = arg.split("=")
            params[key] = value
        elif key != "":
            params[key] += (" " + arg)
    return params

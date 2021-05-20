import os

def get_key():
    try:
        key = os.environ["TOOLCHEST_KEY"]
    except KeyError as e:
        print("Key not found. Please set env var TOOLCHEST_KEY to your specified Toolchest authentication key.")
        return e
    return key

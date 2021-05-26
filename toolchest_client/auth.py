import os

def get_key():
    try:
        key = os.environ["TOOLCHEST_KEY"]
    except KeyError as e:
        print("Key not found. Please set env var TOOLCHEST_KEY to your specified Toolchest authentication key.")
        print("Function call:")
        print("    toolchest_client.set_key(YOUR_KEY_HERE)")
        return e
    return key

def set_key(key):
    if os.path.isfile(key):
        with open(key, "r") as f:
            os.environ["TOOLCHEST_KEY"] = f.read().strip()
    else:
        os.environ["TOOLCHEST_KEY"] = key

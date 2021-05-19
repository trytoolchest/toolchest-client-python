import os

import requests

def query(tool, version, **kwargs):
    """
    TODO: Document
    """

    try:
        key = os.environ["TOOLCHEST_KEY"]
    except KeyError:
        print("Key not found. Please set env var TOOLCHEST_KEY to your specified Toolchest authentication key.")
        return None


    pass

def cutadapt(cutadapt_args, **kwargs):
    query(kwargs)

def kraken2(kraken2_args="", **kwargs):
    query(kwargs)

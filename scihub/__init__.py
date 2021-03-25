import os
import json


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

version_info = json.load(open(os.path.join(BASE_DIR, 'version', 'version.json')))
__version__ = version_info['version']

import os
import sys
import runpy
import importlib

print('STARTUP_SCRIPT: CWD=', os.getcwd())
print('STARTUP_SCRIPT: PYTHONPATH=', os.environ.get('PYTHONPATH'))

try:
    # Try to import the app module and print where it was loaded from
    m = importlib.import_module('campusgo_api.app')
    print('STARTUP_SCRIPT: campusgo_api.app file=', getattr(m, '__file__', None))
except Exception as e:
    print('STARTUP_SCRIPT: import campusgo_api.app failed:', e)

# Exec gunicorn so the container uses the same command but after printing info
args = ['gunicorn', 'campusgo_api.app:app', '--workers', '2', '--bind', '0.0.0.0:$PORT']
print('STARTUP_SCRIPT: exec', args)
os.execvp('gunicorn', args)

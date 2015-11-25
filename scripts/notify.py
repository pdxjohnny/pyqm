import os
import sys
import json
import subprocess

def notify(message, title="Notify"):
    command = [
        "notify-send",
        title,
        message
    ]
    return subprocess.check_output(command)

def build_done(hook):
    notify(json.dumps(hook), "Build done")

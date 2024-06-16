import subprocess
import os
import multiline
import shutil
from dotenv import load_dotenv
import logging
import sys
load_dotenv()
out_stream_handler = logging.StreamHandler(sys.stdout)
out_stream_handler.setLevel(logging.DEBUG)
out_stream_handler.addFilter(lambda record: record.levelno <= logging.INFO)
err_stream_handler = logging.StreamHandler(sys.stderr)
err_stream_handler.setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s', handlers=[out_stream_handler, err_stream_handler])
logging.info("logging configured")

def patch(user_id):
    logging.info("cd to patch dir")
    current_pwd = os.getcwd()
    os.chdir(os.getenv("PATCH_DIR"))
    # first check for updates
    logging.info("checking for updates")
    git = subprocess.Popen(["git", "pull"])
    git.wait()
    if git.returncode != 0 or git.returncode is None:
        logging.error("git pull failed")
        return False
    logging.info("run patch")
    patch = subprocess.Popen(["node", "index.js"])
    patch.wait()
    if patch.returncode != 0 or patch.returncode is None:
        logging.error("patch failed")
        return False
    logging.info("patch done")
    logging.info("read json")
    k = open("settings.json", "r")
    settings = multiline.load(k)
    k.close()
    logging.info(f"filename is {settings['apkFileName']}")
    shutil.move(settings['apkFileName'] + "_Patched.apk", current_pwd+f"/patch-{str(user_id)}.apk")
    os.chdir(current_pwd)
    logging.info("cd back")
    return True

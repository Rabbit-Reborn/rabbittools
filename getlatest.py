import requests
import os
from dotenv import load_dotenv
import sys
import logging
import multiline

load_dotenv()
ota_url = os.getenv("OTA_URL")
out_stream_handler = logging.StreamHandler(sys.stdout)
out_stream_handler.setLevel(logging.DEBUG)
out_stream_handler.addFilter(lambda record: record.levelno <= logging.INFO)
err_stream_handler = logging.StreamHandler(sys.stderr)
err_stream_handler.setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
    handlers=[out_stream_handler, err_stream_handler],
)
logging.info("logging configured")


def getLatestOTA():
    r = requests.get(
        ota_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        },
    )
    logging.info(f"Received response: {r.text}")
    if r.status_code != 200:
        logging.error("failed to get ota")
        return False
    else:
        return multiline.loads(r.text, strict=False)

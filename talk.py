import os
from dotenv import load_dotenv
import sys
import json
import logging
import websockets

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


async def Talk(message):
    try:
        uri = "ws://127.0.0.1:8080"
        return_message = ""
        async with websockets.connect(uri) as websocket:
            logging.info(f"send login")

            login_message = {
                "type": "logon",
                "data": {
                    "imei": os.getenv("IMEI"),
                    "accountKey": os.getenv("ACCOUNT_KEY"),
                },
            }

            await websocket.send(login_message)
            logging.info("sent wait for response")

            response = await websocket.recv()

            logging.info(f"received response: {response}")
            r = json.loads(response)
            if r["data"] != "success":
                logging.error("failed to logon")
                return "login_failure"

            logging.info("login success")

            k = {"type": "message", "data": message}
            await websocket.send(json.dumps(k))
            logging.info("sent message")
            response = await websocket.recv()
            v = json.loads(response)
            logging.info(f"received response: {response}")
            return_message = v["data"]
            await websocket.close()
            return return_message
    except Exception as e:
        logging.error(f"error: {e}")
        return "error"

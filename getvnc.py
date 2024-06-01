import os
import json
import time
import threading
import sys
import logging
from urllib.parse import unquote
from dotenv import load_dotenv
from websockets.sync.client import connect

load_dotenv()
vnc_url = os.getenv("VNC_URL")
vnc_auth = os.getenv("VNC_AUTH")
print(vnc_url)
headers = {
    "Accept-Encoding:" "gzip, deflate, br, zstd"
    "Pragma": "no-cache",
    "Origin": "https://hole.rabbit.tech",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
}
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


out_stream_handler = logging.StreamHandler(sys.stdout)
out_stream_handler.setLevel(logging.DEBUG)
out_stream_handler.addFilter(lambda record: record.levelno <= logging.INFO)
err_stream_handler = logging.StreamHandler(sys.stderr)
err_stream_handler.setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s', handlers=[out_stream_handler, err_stream_handler])
logging.info("logging configured")
def keep_alive(websocket, stop_event):
    try:
        while not stop_event.is_set():
            # Send a ping or some message to keep the connection alive
            websocket.send(json.dumps({"type": "ping"}))
            time.sleep(10)  # Adjust the interval as needed
    except Exception as e:
        logging.error(f"Error in keep_alive thread: {e}")


def getVNC(vnc_type):
    vnc = vnc_url + vnc_type
    init_message = {
        "init": {
            "accessToken": vnc_auth,
            "viewportConfig": {
                "viewportHeight": 938,
                "viewportWidth": 1125
            }
        }
    }
    logging.info("init message configured successfully")
    try:
        logging.info("connecting to vnc url")
        websocket = connect(vnc, additional_headers=headers, user_agent_header=user_agent)
        logging.info("sending vnc init message")
        websocket.send(json.dumps(init_message))
        logging.info("Sent the init message")
        message = websocket.recv(timeout=30)
        logging.info(f"Received: {message}")
        message = json.loads(message)
        if "error" in message:
            websocket.close()
            return False
        else:
            debugNoVncUrl = unquote(message["webReady"]["debugNoVncUrl"], "utf-8")
            logging.info(f"Debug NoVNC URL: {debugNoVncUrl}")

            # Start a thread to keep the connection alive
            logging.info("starting websocket thread")
            stop_event = threading.Event()
            keep_alive_thread = threading.Thread(target=keep_alive, args=(websocket, stop_event), name=f"websocket-keep-alive-{vnc_type}")
            keep_alive_thread.start()

            # Return the URL while the WebSocket connection is kept alive
            logging.info("returning debugNoVncUrl")
            return debugNoVncUrl

            # Sleep for 5 minutes then stop the keep-alive thread
            time.sleep(5 * 60)
            logging.info("Stopping websocket thread")
            stop_event.set()
            keep_alive_thread.join()
            websocket.close()
    except TimeoutError:
        logging.error("Connection timeout while waiting for Rabbit to respond with VNC")
        return "timeout-vnc"
    except Exception as e:
        logging.error(e)
        return False
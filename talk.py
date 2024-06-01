import os
from dotenv import load_dotenv
import sys
import multiline
import logging
from websockets.sync.client import connect

load_dotenv()
socket_url = os.getenv("SOCKET_URL")
proxy_url = os.getenv("PROXY_URL")
out_stream_handler = logging.StreamHandler(sys.stdout)
out_stream_handler.setLevel(logging.DEBUG)
out_stream_handler.addFilter(lambda record: record.levelno <= logging.INFO)
err_stream_handler = logging.StreamHandler(sys.stderr)
err_stream_handler.setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
                    handlers=[out_stream_handler, err_stream_handler])
logging.info("logging configured")

logging.info("Connecting")
aisocket = connect(socket_url,
                   additional_headers={"App-Version": os.getenv("APP_VERSION"), "OS-Version": os.getenv("OS_VERSION")})
logging.info("Connected")
logging.info("authencating")

auth_message = {
    "global": {
        "initialize": {
            "deviceId": os.getenv("IMEI"),
            "evaluate": False,
            "greet": True,
            "language": "en",
            "listening": True,
            "location": {
                "latitude": 0.0,
                "longitude": 0.0
            },
            "mimeType": "wav",
            "timeZone": "GMT",
            "token": "rabbit-account-key+" + os.getenv("ACCOUNT_KEY"),
        }
    }
}

logging.info("Sending auth message")
aisocket.send(multiline.dumps(auth_message))


def sendMessage(message):
    try:
        logging.info(f"Sending message: {message}")
        aisocket.send(multiline.dumps({
            "kernel": {
                "userText": {
                    "text": message
                }
            }
        }))
        message = aisocket.recv(timeout=10)
        logging.info(f"Received: {message}")
        messagejson = multiline.loads(message, strict=False)
        if "assistantResponse" in messagejson["kernel"]:
            return messagejson["kernel"]["assistantResponse"]
        else:
            logging.error("assitance response not found in json. return false!")
            return False
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
        return False

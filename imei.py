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
import random


def validate_imei(imei):
    imei = ''.join(filter(str.isdigit, imei))
    if len(imei) != 15 or not imei.isdigit():
        return False

    imei_without_checksum = imei[:-1]
    checksum = imei[-1]
    if calculate_checksum(imei_without_checksum) == checksum:
        return True
    else:
        return False


def calculate_checksum(imei_without_checksum):
    imei_array = list(map(int, imei_without_checksum))
    sum_digits = 0
    double = False
    for digit in imei_array:
        if double:
            digit *= 2
            if digit > 9:
                digit -= 9
        sum_digits += digit
        double = not double
    checksum = (10 - (sum_digits % 10)) % 10
    return str(checksum)


def generate_imei():
    TAC = "35847631"
    serial_number_prefix = "00"
    serial_number = serial_number_prefix + ''.join(str(random.randint(0, 9)) for _ in range(4))
    imei_without_checksum = TAC + serial_number
    checksum = calculate_checksum(imei_without_checksum)
    generated_imei = imei_without_checksum + checksum
    return generated_imei

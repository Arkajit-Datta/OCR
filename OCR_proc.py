import easyocr 
from PIL import Image
import numpy as np
import logging

def remove_spaces(string) -> str:
    return string.replace(" ","")

def do_ocr(img_path, reader) -> str:
    img = Image.open(img_path)
    logging.info("Started OCR")
    try:
        bounds = reader.readtext(np.array(img),decoder = 'beamsearch', beamWidth=10, paragraph=False, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
        logging.info("OCR Complete")
    except Exception as e:
        logging.exception("Error in OCR")
    captcha = ""
    for bound in bounds:
        captcha += bound[1]
    captcha = remove_spaces(captcha)
    captcha = captcha.upper()
    return captcha
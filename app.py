from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import shutil
import os
from OCR_proc import do_ocr
import easyocr
reader = easyocr.Reader(['en'],gpu = False, model_storage_directory = "Models/.")

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pipeline").setLevel(logging.INFO)

app = FastAPI(title="VIT-Autocaptcha-OCR-functionality", version="1.0.0 beta")

#allowing the API to all the specefic orgins
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
]

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    logging.info("This api is up")
    return JSONResponse(
        status_code=200,
        content={
            "message": "The API is alive"
        }
    )

@app.post("/doOcr/")
def ocr(captchaImg: UploadFile = File(...)):
    path_captcha_storage = "CaptchaImages"
    
    if captchaImg != None:
        captchaImg_filename = captchaImg.filename
        path_captcha_storage_final = os.path.join(path_captcha_storage, captchaImg_filename)
        try:
            logging.info("Storing the Captcha Image")
            with open(path_captcha_storage_final,"wb") as buffer:
                shutil.copyfileobj(captchaImg.file, buffer)  
                logging.info("Captcha saved in storage")   
        except Exception as e:
            logging.error(e)
            logging.error("the file saving process didnt work properly")
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Image coulde not be saved properly",
                    "error_message": -2
                }
            )
    else:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Image not uploaded",
                "error_message": -1
            }
        )
    try:
        captcha_res = do_ocr(path_captcha_storage_final, reader=reader)
    except Exception as e:
        logging.exception("Error in OCR")
        return JSONResponse(
            status_code=404,
            content={
                "message": "Error in OCR",
                "error_message": -4
            }
        )
    return JSONResponse(
        status_code=200,
        content={
            "captcha": captcha_res,
            "message":"Successfull in extracting the captcha"
        }
    )
    
    
if __name__ == "__main__":
    uvicorn.run(
        app,
        port=5000,
        host="127.0.0.1",
    )
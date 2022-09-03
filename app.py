
'''
This branch has to be kept seperate from the main branch
    -> Works as a proxy to the main branch
'''
from email import message
from urllib import response
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import requests
import json 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("pipeline").setLevel(logging.INFO)

app = FastAPI(title="VIT-Autocaptcha-OCR-functionality-proxy", version="1.0.0 beta")

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

#request to recieve the image 
class request_recognise(BaseModel):
    img: str

@app.get("/")
def root():
    logging.info("This api is up")
    return JSONResponse(
        status_code=200,
        content={
            "message": "The API is alive"
        }
    )


@app.post("/aws_proxy")
def aws_proxy(req: request_recognise):
    ocr_url = "https://13.127.18.222/recogniseCaptchaBase64/"
    response = requests.post(ocr_url, verify=False ,json={"img": req.img})
    print(response.text)
    if response.ok:
        result = json.loads(response.text)
        if "error_message" in result:
            error_msg = result["error_message"]
            logging.exception("Error in OCR, Error in the OCR Server")
            return JSONResponse(
                status_code=404,
                content={
                    "message": "Error in OCR",
                    "error_message": error_msg
                }
            )
        else:
            logging.info("Successful OCR in Server Recieved the Results")
            captcha_res = result["captcha"]
            return JSONResponse(
                status_code=200,
                content={
                    "captcha": captcha_res,
                    "message":"Successfull in extracting the captcha"
                }
            )
    else:
        return JSONResponse(
                status_code=404,
                content={
                    "message": "Error in OCR, response from AWS was not recieved",
                    "error_message": -6
                }
            )
            
    
if __name__ == "__main__":
    uvicorn.run(
        app,
        port=5000,
        host="127.0.0.1",
    )
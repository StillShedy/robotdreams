from datetime import datetime
import os
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from pathlib import Path
import json

app = FastAPI()


token =  os.environ['AUTH_TOKEN']

class Validator:
    def is_valid_date(self, date_string, format="%Y-%m-%d") -> bool:
        try:
            datetime.strptime(date_string, format)
            return True
        except ValueError:
            return False

    def is_valid_path(self, path: str, folder: str) -> bool:
        path_segments = list(Path(path).parts)
        return self.is_valid_date(path_segments[len(path_segments) - 1]) and path_segments[len(path_segments) - 2] == folder


class Job_1_Dto(BaseModel):
    date: str
    raw_dir: str

def getData(date: str, page:int) -> list:
    response = requests.get(
        url='https://fake-api-vycpfa6oca-uc.a.run.app/sales',
        params={'date': date, 'page': page},
        headers={'Authorization': token},
    )

    return response.json()


def clean_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            clean_folder(item_path)
            os.rmdir(item_path)

def job_one(dto: Job_1_Dto):
    clean_folder(dto.raw_dir)
    is_running = True
    page = 1
    while(is_running):
        response = getData(dto.date, page)
        is_running = isinstance(response, list)
        if is_running:
            write_json(response, dto.raw_dir, dto.date, page)
            page = page + 1


def write_json(items: list, path:str, date:str, index: int = -1):
    file_name = ''
    if index == -1:
        file_name= os.path.join(path, f"{date}.json")
    else:
        file_name = os.path.join(path, f"{date}_{index}.json")

    with open(file_name, 'w') as file:
        json.dump(items, file)

@app.get("/")
def read_root():
    return {"Hello": "World"}


validator = Validator()

@app.post("/")
def job_one_endpoint(dto: Job_1_Dto):
    errorMessage = ''
    if(validator.is_valid_date(dto.date) == False):
        errorMessage = f"{errorMessage} {dto.date} is not a valid date"
    if(validator.is_valid_path(dto.raw_dir, "raw") == False):
        errorMessage = f"{errorMessage} {dto.raw_dir} is not a valid folder"
    if(len(errorMessage) > 0):
        raise HTTPException(status_code=400, detail=errorMessage)
    else:
        job_one(dto)
        return {"message": "Success"}




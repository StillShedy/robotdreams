import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import fastavro
from datetime import datetime

app = FastAPI()

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


class Job_2_Dto(BaseModel):
    stg_dir : str
    raw_dir: str

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

shema = {
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "client", "type": "string"},
    {"name": "purchase_date", "type": "string"},
    {"name": "product", "type": "string"},
    {"name": "price", "type": "int"}
  ]
}
def job_two(dto: Job_2_Dto):
    clean_folder(dto.stg_dir)
    files = os.listdir(dto.raw_dir)
    for file_path in files:
        file_path_obj = Path(file_path)
        json_path = os.path.join(dto.raw_dir, file_path)
        with open(json_path, 'rb') as file:
            json_data = json.load(file)
            avro_path = os.path.join(dto.stg_dir, f"{file_path_obj.stem}.avro")
            with open(avro_path, 'w') as avro_file:
                fastavro.json_writer(avro_file, shema, json_data)

def read_json(items: list, path:str, date:str, index: int = -1):
    file_name = ''
    if index == -1:
        file_name= f"{path}/{date}.json"
    else:
        file_name = f"{path}/{date}_{index}.json"

    with open(file_name, 'w') as file:
        json.dump(items, file)

@app.get("/")
def read_root():
    return {"Hello": "World"}


validator = Validator()

@app.post("/")
def job_two_endpoint(dto: Job_2_Dto):
    errorMessage = ''
    if(validator.is_valid_path(dto.stg_dir, "stg") == False):
        errorMessage = f"{errorMessage} {dto.date} is not a valid folder"
    if(validator.is_valid_path(dto.raw_dir, "raw") == False):
        errorMessage = f"{errorMessage} {dto.raw_dir} is not a valid folder"
    if(len(errorMessage) > 0):
        raise HTTPException(status_code=400, detail=errorMessage)
    else:
        job_two(dto)
        return {"message": "Success"}




from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pika
import json
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    if save_file(file):
        return {"filename": file.filename,
                "state" : "success"}
    else:
        return {"filename": file.filename,
                "state" : "fail"}

def save_file(file: UploadFile) -> bool:
    with open(f"bucket/{file.filename}", "wb") as bin_file:
        try:
            bin_file.write(file.file.read())

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.getenv("PUBSUB_HOSTNAME"), port=5672))
            channel = connection.channel()
            channel.queue_declare(queue='new_file', durable=True)

            channel.basic_publish(
                exchange='',
                routing_key='new_file',
                body=json.dumps({
                    "file_name": file.filename,
                    "type":"video"
                }),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ))
            print(f"{file.filename} saved")
            connection.close()
        except Exception as err:
            raise(err)

    return True
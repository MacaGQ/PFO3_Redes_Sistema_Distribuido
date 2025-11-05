import pika
import json
import threading
import os
import time
from dotenv import load_dotenv
from database import update_task_status

load_dotenv()

HOST = os.getenv("RABBITMQ_HOST")
QUEUE = os.getenv("RABBITMQ_QUEUE")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBIT_USER = os.getenv("RABBITMQ_USER")
RABBIT_PASS = os.getenv("RABBITMQ_PASSWORD")

def process_task(data):
    task_id = data.get("task_id")
    task = data.get("task")
    print(f"[Worker] procesando tarea: {task}")

    # Simulacion de realización de tarea
    time.sleep(2)
    print(f"[Worker] Tarea completada: {task}")
    
    # Actualizar estado de la tarea en ddbb
    update_task_status(task_id, "Completada")


def callback(channel, method, properties, body):
    data = json.loads(body)
    print(f"{body} recibido")
    threading.Thread(target=process_task, args=(data, )).start()


def start_worker():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    parameters = pika.ConnectionParameters(
        host= HOST,
        port = RABBIT_PORT,
        credentials= credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE)

    print("[Worker] esperando tareas...")

    channel.basic_consume(queue=QUEUE, auto_ack=True, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
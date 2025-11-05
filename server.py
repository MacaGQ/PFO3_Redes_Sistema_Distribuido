import socket
import threading
import json
import bcrypt
import pika
import os
from dotenv import load_dotenv
from database import create_tables, get_user, create_user, get_tasks_user, create_task

load_dotenv()

# Informacion
HOST = os.getenv("POSTGRES_HOST")
PORT = 5000
QUEUE = os.getenv("RABBITMQ_QUEUE")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBIT_USER = os.getenv("RABBITMQ_USER")
RABBIT_PASS = os.getenv("RABBITMQ_PASSWORD")


def init_socket():
    print("Creando socket del servidor")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configuracion con HOST y PUERTO
    print("Socket bind")
    server_socket.bind((HOST, PORT))
    print("Socket listen")
    server_socket.listen(5)

    print(f"Servidor escuchando en {HOST}:{PORT}")

    return server_socket

def conn_accept(socket, channel):
    print("Iniciando conexion...")
    try:
        while True:
            connection, address = socket.accept()
            print(f"Conexion establecida con {address}")

            thread = threading.Thread(target=handle_client, args=(connection, channel))
            thread.start()

    except Exception as e:
        print(f"Error en conn_accept: {e}")

    finally:
        print("Cerrando socket")
        socket.close()


def handle_client(connection, channel):
    try:
        with connection:
            while True:
                data = connection.recv(1024).decode()
                
                if not data:
                    break

                message = json.loads(data)
                action = message.get("action")

                match action:
                    case "register":
                        response = register(message)

                    case "login":
                        response = login(message)

                    case "get_tasks":
                        response = get_tasks(message)

                    case "new_task":
                        message["channel"] = channel
                        response = new_task(message)

                connection.send(json.dumps(response).encode())

    except Exception as e:
        print(f"Error en handle_client: {e}")


def register(message):
    username = message.get("username")

    exists = get_user(username)

    if exists != None:
        print("Usuario en uso")
        return {"status": "in_use"}
       
    else:
        password = message.get("password")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        create_user(username, hashed_password)

        return {"status":"success"}

def login(message):
    username = message.get("username")

    user = get_user(username)

    if not user:
        print("No existe el usuario")
        return {"status": "no_user"}

    password = message.get("password")
    hashed_password = user[2]

    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return {"status": "logged_in"}
    else:
        return {"status": "wrong_credentials"}
    
def get_tasks(message):
    username = message.get("username")

    tasks = get_tasks_user(username)

    if tasks:
        print("Enviando tareas a cliente")
        print(tasks)
        response = {"status": "success", "tasks": tasks}
    else:
        print("No hay tareas")
        print(tasks)
        response = {"status": "no_tasks"}

    return response

def new_task(message):
    username = message.get("username")
    task = message.get("task")
    channel = message.get("channel")

    task_id = create_task(username, task)
    print(task_id)

    if task_id:
        response = {"status": "task_created"}
        data = {"task_id": task_id, "task": task}
        send_to_worker(data, channel)
    else:
        response = {"status": "error"}

    print(response)

    return response
    
def send_to_worker(task, channel):
    body = json.dumps(task)
    channel.basic_publish(exchange='', routing_key='tasks', body=body)
    print("Tarea enviada a [Worker]")

def start_queue():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    parameters = pika.ConnectionParameters(
        host = HOST,
        port= RABBIT_PORT,
        credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE)

    return channel

def start_server():
    try:
        channel = start_queue()
        socket = init_socket()
        conn_accept(socket, channel)
    
    except Exception as e:
        print(f"Error al iniciar servidor: {e}")


if __name__ == "__main__":
    create_tables()
    start_server()


    
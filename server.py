import socket
import threading
import json
import bcrypt
import pika
from database import create_tables, get_user, create_user

# Informacion
HOST = 'localhost'
PORT = 5000
ddbb = 'tasks_db'


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

def conn_accept(socket):
    print("Iniciando conexion...")
    try:
        while True:
            connection, address = socket.accept()
            print(f"Conexion establecida con {address}")

            thread = threading.Thread(target=handle_client, args=(connection,))
            thread.start()

    except Exception as e:
        print(f"Error en conn_accept: {e}")

    finally:
        print("Cerrando socket")
        socket.close()


def handle_client(connection):
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

                # AGREGAR MAS FUNCIONES

                connection.send(json.dumps(response).encode())

    except Exception as e:
        print(f"Error en handle_client: {e}")
        return {"status": "exception"}


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
    

def start_server():
    try:
        socket = init_socket()
        conn_accept(socket)
    
    except Exception as e:
        print(f"Error al iniciar servidor: {e}")


if __name__ == "__main__":
    create_tables()
    start_server()


    
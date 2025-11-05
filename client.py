import socket
import json

# Información
HOST = 'localhost'
PORT = 5000

def send_request(action, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    request = {"action": action, **data}
    client_socket.send(json.dumps(request).encode())

    response = client_socket.recv(1024).decode()
    client_socket.close()

    return response

# Registrarse
def register():
    print("--- REGISTRO ---")
    username = input("Ingrese un nombre de usuario: ")
    password = input("Ingrese una contraseña: ")

    data = {"username": username, "password": password}
    
    print(f"Registrando usuario {username}...")

    response = json.loads(send_request("register", data))

    match response.get("status"):
        case "success":
            print("Usuario creado con exito! Volviendo al menu principal...")

        case "in_use":
            print("ERROR: Usuario ya en uso. Intente con otro usuario o inicie sesión")

        case "exception":
            print("Error del servidor")

    main()

# Iniciar Sesion
def login():
    print("\n--- INICIAR SESION ---\n")
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")

    data = {"username": username, "password": password}

    print(f"\nIniciando Sesión para {username}...\n")

    response = json.loads(send_request("login", data))

    # De acuerdo a response habilitar inicio de sesion o no
    match response.get("status"):
        case "logged_in":
            print(f"\nBienvenido {username}!\n")
            tasks(username)

        case "no_user":
            print(f"\nNo existe un usuario '{username}' registrado. Por favor registrarse\n")
            main()

        case "wrong_credentials":
            print("\nCredenciales incorrectas. Volviendo al menu principal\n")
            main()


# Manejar tareas
def tasks(username):
    print("--- TAREAS ---")
    print("Ingrese una opción")
    print("[1] Ver tareas")
    print("[2] Crear tarea nueva")
    print("[3] Volver atrás")

    while True:
        option = input("Ingrese solo el numero de opcion deseada: ")
        match option:
            case "1":
                send_request("get_tasks", username)
                break
        
            case "2":
                send_request("new_task", username)           

            case "3":
                main()

            case _:
                print("Error. Ingrese solo el número de la opcion deseada")
         

# Menu Principal
def main():
    print("Bienvenido a la App. Ingrese una opcion para continuar")
    print("[1] Registrarse")
    print("[2] Iniciar Sesion")
    print("[3] Salir")

    while True:
        option = input("Ingrese solo el numero de opcion deseada: ")
        match option:
            case "1":
                register()
                break
        
            case "2":
                login()           

            case "3":
                exit

            case _:
                print("Error. Ingrese solo el número de la opcion deseada")

if __name__ == "__main__":
    main()
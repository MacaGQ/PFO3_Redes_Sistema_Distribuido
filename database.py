import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener conexion con postgres para manipular la base de datos
def get_connection():
    print("Conectando con la base de datos...")
    try:
        connection = psycopg2.connect(user = os.getenv("POSTGRES_USER"),
                                      password = os.getenv("POSTGRES_PASSWORD"),
                                      host = os.getenv("POSTGRES_HOST"),
                                      port = os.getenv("POSTGRES_PORT"),
                                      database = os.getenv("POSTGRES_DB")
                                      )
        print("Conectado a la base de datos")
        return connection
    
    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")


# Crear tablas si no existen
def create_tables():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        create_users_query = '''CREATE TABLE IF NOT EXISTS users (
            ID SERIAL PRIMARY KEY,
            username VARCHAR(20) UNIQUE NOT NULL,
            password TEXT NOT NULL)'''

        create_tasks_query = '''CREATE TABLE IF NOT EXISTS tasks (
            ID SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(ID),
            task TEXT NOT NULL,
            status TEXT DEFAULT 'Procesando'
            )'''
        
        cursor.execute(create_users_query)
        cursor.execute(create_tasks_query)

        connection.commit()
        print("Tablas creadas con exito")

    except Exception as e:
        print(f"Error al crear la tablas: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Desconectado de la base de datos")


# Crear usuario nuevo
def create_user(username, password):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        new_user_query = """INSERT INTO users (username, password) VALUES (%s, %s)"""

        cursor.execute(new_user_query, (username, password))

        connection.commit()
        print(f"Usuario {username} creado con exito")

    except Exception as e:
        print(f"Error al crear usuario: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Desconectado de la base de datos")


# Buscar usuario por el username 
def get_user(username):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        get_user_query = "SELECT ID, username, password FROM users WHERE username = %s"
        
        cursor.execute(get_user_query, (username,))
        user = cursor.fetchone()

        if user:
            return user
        else:
            return None
        
    except Exception as e:
        print(f"Error al buscar usuario: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Desconectado de la base de datos")


# Crear tarea
def create_task(username, task):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        user = get_user(username)
        user_id = user[0]

        new_task_query = '''INSERT INTO tasks (user_id, task) VALUES (%s, %s) RETURNING ID'''
        
        cursor.execute(new_task_query, (user_id, task))

        task_id = cursor.fetchone()[0]

        connection.commit()

        print(task_id)

        print(f"Tarea {task} creada con exito para el usuario {username}")
        return task_id
        
    except Exception as e:
        print(f"Error al crear tarea: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Desconectado de la base de datos")


# Cambiar estado de una tarea completada
def update_task_status(task_id, status):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        update_status_query = '''UPDATE tasks SET status = %s WHERE ID = %s'''
        
        cursor.execute(update_status_query, (status, task_id))

        print(f"Estado de la tarea {task_id} actualizado a {status}")

    except Exception as e:
        print(f"Error al actualizar estado de la tarea {task_id}: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Desconectado de la base de datos")

        
# Ver las tareas del usuario activo
def get_tasks_user(username):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        user = get_user(username)
        user_id = user[0]

        get_tasks_query = '''SELECT * FROM tasks WHERE user_id = %s'''

        cursor.execute(get_tasks_query, (username,))
        tasks = cursor.fetchall()

        return tasks      

    except Exception as e:
        print(f"Error al obtener tareas de {username}: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Desconectado de la base de datos")



        




        
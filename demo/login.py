import pygame
from pygame.locals import *
import sys
import os
from datetime import datetime
import pymysql
from dotenv import load_dotenv

# Cargar variables de entorno para la conexión a la base de datos
load_dotenv()

# Función para conectar a la base de datos
def get_db_connection():
    try:
        return pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT'))
        )
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Función principal del juego
def main():
    pygame.init()

    # Crear la ventana del juego
    game_width = 500
    game_height = 500
    size = (game_width, game_height)
    game = pygame.display.set_mode(size)
    pygame.display.set_caption('Pokemon')

    # Fuentes
    font = pygame.font.Font(None, 36)

    # Definir colores
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Cargar fondo
    background = pygame.image.load('fondo7.png')
    background = pygame.transform.scale(background, (game_width, game_height))

    # Variables para el Login
    global username, is_logged_in, input_active
    username = ""
    is_logged_in = False
    input_active = False



    # Función para registrar cambios en el log
    def log_change(username, action):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO Historial (fecha, usuario, tipo_evento) VALUES (%s, %s, %s)",
                                   (timestamp, username, action))
                    connection.commit()
            finally:
                connection.close()

    def upsert_user(username):
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Primero, verificar si el usuario ya existe
                    cursor.execute("SELECT * FROM Usuarios WHERE nombre_usuario = %s", (username,))
                    existing_user = cursor.fetchone()

                    if existing_user:  # Si el usuario ya existe, actualizar la hora de registro
                        cursor.execute("UPDATE Usuarios SET hora_registro = %s WHERE nombre_usuario = %s",
                                       (datetime.now(), username))
                        print(f"Usuario {username} ya existe, hora de registro actualizada.")
                    else:  # Si no existe, crear un nuevo usuario
                        cursor.execute(
                            "INSERT INTO Usuarios (nombre_usuario, email, contraseña, hora_registro) VALUES (%s, %s, %s, %s)",
                            (username, 'email@example.com', 'default_password', datetime.now()))
                        print(f"Usuario {username} creado.")

                    # Confirmar los cambios
                    connection.commit()

            finally:
                connection.close()

    # Función para mostrar la pantalla de login
    def login_screen():
        global username, is_logged_in, input_active

        while not is_logged_in:
            game.fill(white)  # Fondo blanco

            # Mostrar texto
            login_text = font.render("Login / Registro", True, black)
            game.blit(login_text, (game_width // 2 - 100, 50))

            # Mostrar etiqueta "Usuario:"
            user_label = font.render("Usuario:", True, black)
            game.blit(user_label, (game_width // 2 - 100, 150))

            # Rectángulo para el campo de entrada
            input_rect = pygame.Rect(game_width // 2 - 100, 200, 200, 40)
            pygame.draw.rect(game, black, input_rect, 2)  # Contorno negro del rectángulo

            # Mostrar texto del usuario en el campo de entrada
            user_text = font.render(username, True, black)
            game.blit(user_text, (input_rect.x + 5, input_rect.y + 5))  # Texto en el campo

            # Botón "Comienza"
            button_text = font.render("Empezar", True, white)
            button_rect = pygame.Rect(game_width // 2 - 60, 300, 120, 50)
            pygame.draw.rect(game, (0, 0, 255), button_rect)  # Botón azul
            game.blit(button_text, (button_rect.x + 6, button_rect.y + 10))  # Texto en el botón

            pygame.display.flip()

            # Capturar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Presionar Enter
                        if username:  # Si el campo de usuario no está vacío
                            upsert_user(username)  # Crear o actualizar usuario
                            log_change(username, "Inicio de sesión o registro")  # Log de inicio de sesión o registro
                            is_logged_in = True  # Iniciar sesión después del registro o inicio de sesión
                    elif event.key == pygame.K_BACKSPACE:  # Borrar el último carácter
                        username = username[:-1]

                    # Agregar caracteres al nombre de usuario si el campo está activo
                    if input_active and event.unicode.isprintable() and len(username) < 20:
                        username += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:  # Manejar clics del mouse
                    if event.button == 1:  # Clic izquierdo
                        if input_rect.collidepoint(event.pos):  # Si el clic es en el campo de entrada
                            input_active = True  # Activar el campo de entrada
                        else:
                            input_active = False  # Desactivar el campo si se hace clic fuera

                        if button_rect.collidepoint(event.pos):  # Si el botón es clickeado
                            if username:  # Si el campo de usuario no está vacío
                                upsert_user(username)  # Crear o actualizar usuario
                                log_change(username,
                                           "Inicio de sesión o registro")  # Log de inicio de sesión o registro
                                is_logged_in = True  # Iniciar sesión después del registro

    # Llamar a la pantalla de login
    login_screen()

    # Resto de tu código para la clase Move, Pokemon y la lógica del juego aquí...

    # Al final de la batalla, guarda el resultado en la base de datos
    def save_battle_result(winner, loser):
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO batalla (ganador, perdedor, fecha) VALUES (%s, %s, %s)",
                                   (winner, loser, datetime.now()))
                    connection.commit()
            finally:
                connection.close()

# Ejecutar el juego
if __name__ == "__main__":
    main()

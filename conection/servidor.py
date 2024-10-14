import socket
import pygame
import pickle
import threading
import time

# Configuración de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Parámetros de la pelota
BALL_RADIUS = 20
BALL_COLOR = (255, 0, 0)
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_speed_x = 3
ball_speed_y = 3

# Lista para almacenar los clientes conectados
clients = []

# Configuración del servidor
HOST = '192.168.18.233'
PORT = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Función que maneja a cada cliente conectado
def handle_client(conn, addr):
    print(f"Cliente conectado: {addr}")
    while True:
        try:
            # Enviar la posición de la pelota a los clientes
            ball_data = {'x': ball_x, 'y': ball_y}
            conn.sendall(pickle.dumps(ball_data))
            time.sleep(1/FPS)
        except:
            print(f"Cliente desconectado: {addr}")
            clients.remove(conn)
            conn.close()
            break

# Hilo para aceptar clientes
def accept_clients():
    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr)).start()

# Hilo para mover la pelota
def move_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    while True:
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Rebote en los bordes
        if ball_x - BALL_RADIUS < 0 or ball_x + BALL_RADIUS > SCREEN_WIDTH:
            ball_speed_x = -ball_speed_x
        if ball_y - BALL_RADIUS < 0 or ball_y + BALL_RADIUS > SCREEN_HEIGHT:
            ball_speed_y = -ball_speed_y

        time.sleep(1/FPS)

# Iniciar el servidor
if __name__ == "__main__":
    threading.Thread(target=accept_clients).start()
    threading.Thread(target=move_ball).start()
    print(f"Servidor escuchando en {HOST}:{PORT}")

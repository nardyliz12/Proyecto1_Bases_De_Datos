import socket
import pygame
import pickle

# Configuración de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Configuración del cliente
HOST = '192.168.18.233'
PORT = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cliente Pygame")
clock = pygame.time.Clock()

# Función principal del cliente
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Recibir datos del servidor
        try:
            data = client_socket.recv(1024)
            ball_data = pickle.loads(data)
        except:
            print("Conexión cerrada por el servidor")
            running = False
            break

        # Limpiar la pantalla
        screen.fill((0, 0, 0))

        # Dibujar la pelota
        pygame.draw.circle(screen, (255, 0, 0), (ball_data['x'], ball_data['y']), 20)

        # Actualizar la pantalla
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    client_socket.close()

if __name__ == "__main__":
    main()

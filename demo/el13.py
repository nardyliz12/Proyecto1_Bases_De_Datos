import csv
import pygame
from pygame.locals import *
import time
import math
import random
import sys
import io
from urllib.request import urlopen
import pymysql.cursors
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT')),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
game_width = 500
game_height = 500
margin_width = 800
margin_height = 500
button_width, button_height = 100, 50
yes_button_rect = pygame.Rect((100, 400), (button_width, button_height))  # Posición y tamaño del botón "Yes"
no_button_rect = pygame.Rect((300, 400), (button_width, button_height))  # Posición y tamaño del botón "No"

button_width, button_height = 50, 50
buttons = {
    "up": pygame.Rect(650, 325, button_width, button_height),
    "down": pygame.Rect(650, 425, button_width, button_height),
    "left": pygame.Rect(600, 375, button_width, button_height),
    "right": pygame.Rect(700, 375, button_width, button_height),
}

# Crear la ventana del juego
game = pygame.display.set_mode((margin_width, margin_height))
pygame.display.set_caption('Pokemon')

# Fuentes
font = pygame.font.Font(None, 36)

background = pygame.image.load('fondo7.png')
background = pygame.transform.scale(background, (game_width, game_height))

# Definir colores
black = (0, 0, 0)
white = (255, 255, 255)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)

button_color = (100, 100, 100)
hover_color = (150, 150, 150)

username = ""
is_logged_in = False
input_active = False

filename = 'usuarios.csv'
base_url = 'https://pokeapi.co/api/v2'
in_login_screen = True

def save_selection_to_csv(filename, username, pokemon_name):
    with open(filename, mode='a', newline='') as file:  # Abrir en modo 'append'
        writer = csv.writer(file)
        writer.writerow([username, pokemon_name])

def draw_movement_buttons():
    mouse_pos = pygame.mouse.get_pos()
    for direction, rect in buttons.items():
        color = hover_color if rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, color, rect)  # Dibujar botón
        if direction == "up":
            pygame.draw.polygon(screen, (0, 0, 0), [(rect.centerx, rect.top), (rect.left, rect.bottom), (rect.right, rect.bottom)])
        elif direction == "down":
            pygame.draw.polygon(screen, (0, 0, 0), [(rect.centerx, rect.bottom), (rect.left, rect.top), (rect.right, rect.top)])
        elif direction == "left":
            pygame.draw.polygon(screen, (0, 0, 0), [(rect.left, rect.centery), (rect.right, rect.top), (rect.right, rect.bottom)])
        elif direction == "right":
            pygame.draw.polygon(screen, (0, 0, 0), [(rect.right, rect.centery), (rect.left, rect.top), (rect.left, rect.bottom)])

def handle_movement_buttons():
    if player_pokemon:  # Asegurarse de que player_pokemon no sea None
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            player_pokemon.y -= 10
        if keys[K_DOWN]:
            player_pokemon.y += 10
        if keys[K_LEFT]:
            player_pokemon.x -= 10
        if keys[K_RIGHT]:
            player_pokemon.x += 10

def create_user_file(filename):
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["usuario"])

def read_users_from_csv(filename):
    users = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        try:
            next(reader)
        except StopIteration:
            return users
        for row in reader:
            users.append(row[0])
    return users



def login_screen():
    global username, is_logged_in, input_active

    valid_users = read_users_from_csv(filename)

    while not is_logged_in:
        game.fill(white)
        pygame.draw.rect(game, black, (margin_width // 2 - game_width // 2, margin_height // 2 - game_height // 2, game_width, game_height), 2)
        login_text = font.render("Login / Registro", True, black)
        game.blit(login_text, (margin_width // 2 - 100, margin_height // 2 - game_height // 2 + 20))
        user_label = font.render("Usuario:", True, black)
        game.blit(user_label, (margin_width // 2 - 100, margin_height // 2 - game_height // 2 + 80))
        input_rect = pygame.Rect(margin_width // 2 - 100, margin_height // 2 - game_height // 2 + 120, 200, 40)
        pygame.draw.rect(game, black, input_rect, 2)
        user_text = font.render(username, True, black)
        game.blit(user_text, (input_rect.x + 5, input_rect.y + 5))
        button_text = font.render("Empezar", True, white)
        button_rect = pygame.Rect(margin_width // 2 - 60, margin_height // 2 - game_height // 2 + 180, 120, 50)
        pygame.draw.rect(game, (0, 0, 255), button_rect)
        game.blit(button_text, (button_rect.x + 6, button_rect.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username in valid_users:
                        is_logged_in = True
                    elif username:

                        valid_users.append(username)
                        is_logged_in = True
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                if input_active and event.unicode.isprintable() and len(username) < 20:
                    username += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False
                    if button_rect.collidepoint(event.pos):
                        if username in valid_users:
                            is_logged_in = True
                        elif username:

                            valid_users.append(username)
                            is_logged_in = True

class Move():
    def __init__(self, name,power,move_type):
        self.name = name
        self.power = power
        self.type = move_type
        print(f"Movimiento creado: {self.name}, Poder: {self.power}, Tipo: {self.type}")


class Pokemon(pygame.sprite.Sprite):
    def __init__(self, name, level, x, y):
        pygame.sprite.Sprite.__init__(self)

        # call the pokemon API endpoint
        # Conectarse a la base de datos
        self.connection = get_db_connection()
        if not self.connection:
            raise Exception("No se pudo conectar a la base de datos.")
        self.cursor = self.connection.cursor()
        # Obtener los datos del Pokémon desde la base de datos
        self.data = self.get_pokemon_data_from_db(name)
        if not self.data:
            raise ValueError(f"Pokémon {name} no encontrado en la base de datos")

        # Obtener datos de la API para los sprites
        self.json = self.get_pokemon_data_from_api(name)

        # Inicializar atributos con los datos obtenidos de la base de datos
        self.name = self.data['nombre_pokemon']
        self.level = level
        self.x = x
        self.y = y
        self.num_potions = 3
        self.max_hp = self.data['HP'] + self.level
        self.current_hp = self.max_hp
        self.attack = self.data['ataque']
        self.defense = self.data['defensa']
        self.speed = self.data['speed']
        self.types = self.data['tipo'].split('/')
        self.size = 150

        # set the sprite to the front facing sprite
        self.set_sprite('front_default')
        self.set_moves()

    def get_pokemon_data_from_db(self, name):
        """Obtiene los datos del Pokémon desde la base de datos."""
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM pokemon WHERE nombre_pokemon = '{name}'")
        return cursor.fetchone()

    def get_pokemon_data_from_api(self, name):
        """Función para obtener datos del Pokémon desde la API."""
        url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Devuelve los datos en formato JSON
        else:
            raise ValueError(f"No se pudo obtener datos de la API para {name}. Status code: {response.status_code}")


    def perform_attack(self, other, move):
        display_message(f'{self.name} utiliza {move.name}')
        time.sleep(2)
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        if move.type in self.types:
            damage *= 1.5
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
        damage = math.floor(damage)
        other.take_damage(damage)

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def use_potion(self):
        if self.num_potions > 0:
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
            self.num_potions -= 1

    def set_sprite(self, side):
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()

        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def set_moves(self):

        self.moves = []
        try:
            print(f"Obteniendo movimientos para Pokémon: {self.data['nombre_pokemon']} (Nivel: {self.level})")

            query = f"""
                    SELECT a.nombre_ataque AS name, a.daño AS power, a.tipo AS type, a.level
                    FROM pokemon p
                    JOIN pokemon_has_ataque pha ON p.id_pokemon = pha.pokemon_id_pokemon
                    JOIN Ataque a ON pha.ataque_id_ataque = a.id_ataque
                    WHERE p.nombre_pokemon = '{self.data['nombre_pokemon']}'
                    AND a.level <= {self.level}
                        """

            # Ejecutar la consulta sin el filtrado de nivel
            self.cursor.execute(query)
            moves_data = self.cursor.fetchall()
            print(moves_data)  # Imprimir los datos obtenidos

            # Ahora aplicamos el filtro de nivel
            moves_data = [move for move in moves_data if move['power'] is not None and move['level'] <= self.level]

            if len(moves_data) == 0:
                print(f"No se encontraron movimientos para {self.data['nombre_pokemon']} en la base de datos.")
            else:
                for move_data in moves_data:
                    move = Move(move_data['name'], move_data['power'], move_data['type'])
                    self.moves.append(move)

                if len(self.moves) > 4:
                    self.moves = random.sample(self.moves, 4)

        except Exception as e:
            print(f"Error obteniendo movimientos desde la base de datos: {e}")

    def draw(self, alpha=255):
        sprite = self.image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))


    def draw_hp(self):
        hp_background = pygame.image.load('barra2.png')  # Asegúrate de que esta ruta sea correcta
        hp_background = pygame.transform.scale(hp_background,
                                               (180, 60))  # Ajusta el tamaño de acuerdo a las barras de HP

        # Dibuja el fondo detrás de la barra de HP
        game.blit(hp_background, (self.hp_x - 10, self.hp_y - 10))  # Ajusta la posición según necesites

        # display the health bar
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)

        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar)

        # display "HP" text
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        game.blit(text, text_rect)

    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def display_message(message):
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    pygame.display.update()

def draw_buttons():
    pygame.draw.rect(game, (0, 255, 0), yes_button_rect)
    pygame.draw.rect(game, (255, 0, 0), no_button_rect)
    font = pygame.font.Font(None, 36)
    yes_text = font.render("Yes", True, (255, 255, 255))
    no_text = font.render("No", True, (255, 255, 255))
    game.blit(yes_text, (yes_button_rect.x + 25, yes_button_rect.y + 10))
    game.blit(no_text, (no_button_rect.x + 25, no_button_rect.y + 10))

def create_button(width, height, left, top, text_cx, text_cy, label):
    mouse_cursor = pygame.mouse.get_pos()
    button = Rect(left, top, width, height)

    # Resaltar el botón si el mouse está sobre él
    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)

    # Añadir la etiqueta al botón
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)

    return button

def draw_message():
    font = pygame.font.Font(None, 48)
    message = font.render("¿Quieres volver a jugar?", True, (255, 255, 255))
    game.blit(message, (game_width // 2 - message.get_width() // 2, 300))

login_screen()
pygame.time.delay(6)
level = 30

# Crear los Pokémon iniciales
bulbasaur = Pokemon('Bulbasaur', level, 20, 150)
charmander = Pokemon('Charmander', level, 170, 150)
squirtle = Pokemon('Squirtle', level, 320, 150)
pikachu = Pokemon('Pikachu', level, 20, 300)
jigglypuff = Pokemon('Jigglypuff', level, 170, 300)
rattata = Pokemon('Rattata', level, 320, 300)
eevee = Pokemon('Eevee', level, 20, 450)
oddish = Pokemon('Oddish', level, 170, 450)
pidgey = Pokemon('Pidgey', level, 320, 450)

# Lista de Pokémon
pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, rattata, eevee, oddish, pidgey]
selected_index = 0
game_status = 'select pokemon'
player_pokemon = None
rival_pokemon = None

button_clicked = False  # Variable para manejar el clic en botones
selection_message = ""  # Variable para el mensaje de selección
timer = 30  # Temporizador inicial
# Variables de estado para las acciones de "Fight" y "Potion"
selected_action = 0  # 0 para Fight, 1 para Potion
actions = ['Fight', 'Potion']

while game_status != 'quit':
    screen.fill(white)

    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'

        if event.type == MOUSEBUTTONDOWN:
                    mouse_click = event.pos
                    # Selección entre "Fight" y "Potion" en el estado 'player turn'
                    if game_status == 'player turn':
                        if fight_button.collidepoint(mouse_click):
                            game_status = 'player move'  # Cambia a seleccionar movimiento
                        elif potion_button.collidepoint(mouse_click):
                            if player_pokemon.num_potions == 0:
                                display_message('No more potions left')
                                time.sleep(2)
                                game_status = 'player move'
                            else:
                                player_pokemon.use_potion()
                                display_message(f'{player_pokemon.name} used potion')
                                time.sleep(2)
                                game_status = 'rival turn'

                    # Selección de movimientos del jugador en el estado 'player move'
                    elif game_status == 'player move':
                        player_pokemon.draw()
                        rival_pokemon.draw()
                        player_pokemon.draw_hp()
                        rival_pokemon.draw_hp()

                        # check which move button was clicked
                        for i in range(len(move_buttons)):
                            button = move_buttons[i]

                            if button.collidepoint(mouse_click):
                                move = player_pokemon.moves[i]
                                player_pokemon.perform_attack(rival_pokemon, move)

                                # check if the rival's pokemon fainted
                                if rival_pokemon.current_hp == 0:
                                    game_status = 'fainted'
                                else:
                                    game_status = 'rival turn'

    # Dibuja los botones de movimiento
    draw_movement_buttons()

    # Dibuja el botón "Enter"
    enter_button_rect = pygame.Rect(550, 250, 50, 50)
    pygame.draw.rect(screen, (0, 0, 255), enter_button_rect)
    enter_text = font.render("E", True, white)
    screen.blit(enter_text, (enter_button_rect.x + 15, enter_button_rect.y + 10))

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0]:  # Si se presiona el botón izquierdo del mouse
        if buttons["left"].collidepoint(mouse_pos) and not button_clicked:
            selected_index = (selected_index - 1) % len(pokemons)
            button_clicked = True  # Marcar que se hizo clic
        elif buttons["right"].collidepoint(mouse_pos) and not button_clicked:
            selected_index = (selected_index + 1) % len(pokemons)
            button_clicked = True  # Marcar que se hizo clic
        elif buttons["up"].collidepoint(mouse_pos) and not button_clicked:  # Mover hacia arriba
            selected_index = (selected_index - 3) % len(pokemons)
            button_clicked = True
        elif buttons["down"].collidepoint(mouse_pos) and not button_clicked:  # Mover hacia abajo
            selected_index = (selected_index + 3) % len(pokemons)
            button_clicked = True
        elif enter_button_rect.collidepoint(mouse_pos) and not button_clicked:  # Clic en el botón "Enter"
            player_pokemon = pokemons[selected_index]
            # Asignar el Pokémon del rival
            rival_pokemon = pokemons[(selected_index + 1) % len(pokemons)]

            # Reducir el nivel del Pokémon rival para hacer la batalla más fácil
            rival_pokemon.level = int(rival_pokemon.level * 0.75)

            # Establecer las coordenadas de las barras de HP
            player_pokemon.hp_x = 275
            player_pokemon.hp_y = 250
            rival_pokemon.hp_x = 50
            rival_pokemon.hp_y = 50
            save_selection_to_csv('pokemon_seleccionado.csv', username, player_pokemon.name)
            # Cambiar el estado del juego a 'prebattle'
            game_status = 'prebattle'

            button_clicked = True  # Marcar que se hizo clic
    else:
        button_clicked = False  # Reiniciar si no se está presionando el botón

    if game_status == 'select pokemon':
        for index, pokemon in enumerate(pokemons):
            x = 20+ (index % 3) * 150  # Calcular la posición x
            y = 20 + (index // 3) * 150  # Calcular la posición y
            pokemon.x = x
            pokemon.y = y
            pokemon.draw()
            if index == selected_index:
                pygame.draw.rect(screen, gold, pokemon.get_rect(), 4)

        # Mostrar el temporizador
        timer_text = font.render(str(int(timer)), True, black)
        screen.blit(timer_text, (width - 50, 10))  # Mostrar en la esquina superior derecha

        # Actualizar temporizador
        if timer > 0:
            timer -= 1 / 30  # Disminuir el temporizador (30 FPS)
        else:
            selection_message = "Tiempo agotado. Selección automática."
            player_pokemon = pokemons[selected_index]
            rival_pokemon = pokemons[(selected_index + 1) % len(pokemons)]

            # Reducir el nivel del Pokémon rival para hacer la batalla más fácil
            rival_pokemon.level = int(rival_pokemon.level * 0.75)
            player_pokemon.hp_x = 275
            player_pokemon.hp_y = 250
            rival_pokemon.hp_x = 50
            rival_pokemon.hp_y = 50
            save_selection_to_csv('pokemon_seleccionado.csv', username, player_pokemon.name)
            game_status = 'prebattle'  # Cambiar a la fase de batalla
        pygame.display.update()
        # get moves from the API and reposition the pokemons
    if game_status == 'prebattle':
        # Dibuja el Pokémon seleccionado
        game.fill(white)
        # set the coordinates of the hp bars

        player_pokemon.draw()
        pygame.display.update()

        # Asegúrate de que rival_pokemon esté definido antes de llamar a set_moves
        if rival_pokemon is None:
            # Aquí puedes inicializar rival_pokemon, por ejemplo, eligiendo un Pokémon aleatorio
            rival_pokemon = random.choice(pokemons)  # Elige un rival aleatorio de la lista

        player_pokemon.set_moves()  # Obtener movimientos del jugador
        rival_pokemon.set_moves()  # Obtener movimientos del rival

        # Reposicionar los Pokémon
        player_pokemon.x = -50
        player_pokemon.y = 100
        rival_pokemon.x = 250
        rival_pokemon.y = -50

        # Redimensionar los sprites
        player_pokemon.size = 300
        rival_pokemon.size = 300
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')

        # Cambiar el estado del juego para iniciar la batalla
        game_status = 'start battle'

    if game_status == 'start battle':

        # rival sends out their pokemon
        alpha = 0
        while alpha < 255:
            game.fill(white) # fondo
            rival_pokemon.draw(alpha)
            display_message(f'Rival sent out {rival_pokemon.name}!')
            alpha += .4

            pygame.display.update()

        # pause for 1 second
        time.sleep(1)

        # player sends out their pokemon
        alpha = 0
        while alpha < 255:
            game.fill(white)
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4

            pygame.display.update()

         # draw the hp bars
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        # determine who goes first
        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'

        pygame.display.update()

        # pause for 1 second
        time.sleep(1)

    # display the fight and use potion buttons
    if game_status == 'player turn':
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        # create the fight and use potion buttons
        fight_button = create_button(240, 140, 10, 350, 130, 412, 'Fight')
        potion_button = create_button(240, 140, 250, 350, 370, 412, f'Use Potion ({player_pokemon.num_potions})')

        # draw the black border
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()

    # display the move buttons
    if game_status == 'player move':

        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        # create a button for each move
        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                   move.name.capitalize())
            move_buttons.append(button)

        # draw the black border
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()

    # rival selects a random move to attack with
    if game_status == 'rival turn':

        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        # empty the display box and pause for 2 seconds before attacking
        display_message('')
        time.sleep(2)

        # select a random move
        move = random.choice(rival_pokemon.moves)
        rival_pokemon.perform_attack(player_pokemon, move)

        # check if the player's pokemon fainted
        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'

        pygame.display.update()

    # one of the pokemons fainted
    if game_status == 'fainted':

        alpha = 255
        while alpha > 0:

            game.fill(white)
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()

            # determine which pokemon fainted
            if rival_pokemon.current_hp == 0:
                player_pokemon.draw()
                rival_pokemon.draw(alpha)
                display_message(f'{rival_pokemon.name} fainted!')
            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                display_message(f'{player_pokemon.name} fainted!')
            alpha -= .4

            pygame.display.update()

        game_status = 'gameover'

    # gameover screen
    if game_status == 'gameover':
        timer_limit = 10  # El límite del temporizador en segundos
        if 'start_time' not in locals():  # Comprobar si start_time ya fue definido
            start_time = pygame.time.get_ticks()  # Registrar el tiempo al entrar en 'gameover'

        # Calcular el tiempo transcurrido desde que se inició el temporizador
        current_time = pygame.time.get_ticks()  # Obtener el tiempo actual
        elapsed_time = (current_time - start_time) / 1000  # Convertir a segundos
        time_left = max(0, timer_limit - int(elapsed_time))  # Asegurar que no sea negativo

        game.fill((0, 0, 0))  # Fondo negro
        draw_buttons()
        draw_message()
        # Mostrar el temporizador en la esquina superior izquierda
        timer_text = font.render(f'Tiempo restante: {time_left}', True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Detectar clics de mouse
            elif event.type == MOUSEBUTTONDOWN:
                if yes_button_rect.collidepoint(event.pos):
                    # Reiniciar el juego seleccionando "Sí"
                    bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
                    charmander = Pokemon('Charmander', level, 175, 150)
                    squirtle = Pokemon('Squirtle', level, 325, 150)
                    pikachu = Pokemon('Pikachu', level, 25, 300)
                    jigglypuff = Pokemon('Jigglypuff', level, 175, 300)
                    rattata = Pokemon('Rattata', level, 325, 300)
                    eevee = Pokemon('Eevee', level, 25, 450)
                    oddish = Pokemon('Oddish', level, 175, 450)
                    pidgey = Pokemon('Pidgey', level, 325, 450)

                    # Actualizar la lista de Pokémon
                    pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, rattata, eevee, oddish, pidgey]
                    game_status = 'select pokemon'
                    start_time = pygame.time.get_ticks()  # Reiniciar el tiempo
                elif no_button_rect.collidepoint(event.pos):
                    # Si el botón "No" es clicado, salir del juego
                    game_status = 'quit'
                    running = False

        # Si el tiempo llega a 0, reiniciar automáticamente
        if time_left <= 0:  # Asegurarte de usar <= para asegurarte de que se reinicie
            # Reiniciar Pokémon automáticamente
            bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
            charmander = Pokemon('Charmander', level, 175, 150)
            squirtle = Pokemon('Squirtle', level, 325, 150)
            pikachu = Pokemon('Pikachu', level, 25, 300)
            jigglypuff = Pokemon('Jigglypuff', level, 175, 300)
            rattata = Pokemon('Rattata', level, 325, 300)
            eevee = Pokemon('Eevee', level, 25, 450)
            oddish = Pokemon('Oddish', level, 175, 450)
            pidgey = Pokemon('Pidgey', level, 325, 450)

            # Actualizar la lista de Pokémon
            pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, rattata, eevee, oddish, pidgey]
            game_status = 'select pokemon'
            start_time = pygame.time.get_ticks()  # Reiniciar el tiempo

        # Actualizar la pantalla al final del bucle
        pygame.display.flip()

    pygame.display.flip()
    pygame.time.delay(30)
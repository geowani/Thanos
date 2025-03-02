import pygame
import random
import os
import sys
from collections import deque

# Configuración del juego
TILE_SIZE = 100
GRID_SIZE = 4
SCREEN_SIZE = TILE_SIZE * GRID_SIZE
FPS = 10  

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TEXT_COLOR = (0, 0, 0) 

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE + 100, SCREEN_SIZE + 100), pygame.RESIZABLE)
pygame.display.set_caption("Mundo de Thanos")

# Cargar icono
icon_img = pygame.image.load("assets/Logo.ico")
pygame.display.set_icon(icon_img)  

clock = pygame.time.Clock()

# Función para cargar imágenes
def load_image(name):
    if not os.path.exists(name):
        print(f"⚠️ Error: No se encontró la imagen en {name}")
        return pygame.Surface((TILE_SIZE, TILE_SIZE))
    img = pygame.image.load(name)
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

# Cargar imágenes desde la carpeta assets
aventurero_img = load_image("assets/Iron.png")
wumpus_img = load_image("assets/Thanos.png")
tesoro_img = load_image("assets/Tesoro.png")
pozo_img = load_image("assets/negro.png")
viento_img = load_image("assets/Viento.png")
olor_img = load_image("assets/Olor.png")

# Fuente para texto
font = pygame.font.SysFont('Arial', 18) 
large_font = pygame.font.SysFont('Arial', 36)  
title_font = pygame.font.SysFont('Arial', 48)  

# Implementación del algoritmo BFS
def bfs(start, goal, size, obstacles):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = deque([(start, [])])  # (posición actual, camino recorrido)
    visited = set()
    visited.add(start)
    
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in visited and (nx, ny) not in obstacles:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(dx, dy)]))
    
    return []  # Si no se encuentra camino

# Clase de juego principal (WumpusWorld)
class WumpusWorld:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.init_world()
        self.player_pos = self.entry_point
        self.game_over = False
        self.treasure_collected = False
        self.death_info = None
        
        # Encontrar el camino hacia la salida
        self.path_to_exit = bfs(self.player_pos, self.exit_point, self.size, 
                                [self.wumpus_pos, self.treasure_pos] + self.pit_positions + self.wind_positions + self.odor_positions)
        self.path_index = 0  # Índice del siguiente movimiento en el camino

    def init_world(self):
        self.entry_point = (0, 0)
        self.exit_point = (self.size - 1, self.size - 1)
        self.wumpus_pos = self.place_randomly(exclude=[self.entry_point, self.exit_point])
        self.treasure_pos = self.place_randomly(exclude=[self.entry_point, self.exit_point, self.wumpus_pos])
        self.pit_positions = [self.place_randomly(exclude=[self.entry_point, self.exit_point, self.wumpus_pos, self.treasure_pos]) for _ in range(2)]
        self.wind_positions = self.generate_wind_positions()
        self.odor_positions = self.generate_odor_positions()
    
    def place_randomly(self, exclude=[]):
        while True:
            pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
            if pos not in exclude and not self.is_nearby_entry_or_exit(pos):
                return pos
    
    def is_nearby_entry_or_exit(self, pos):
        entry_x, entry_y = self.entry_point
        exit_x, exit_y = self.exit_point
        return abs(pos[0] - entry_x) <= 1 and abs(pos[1] - entry_y) <= 1 or abs(pos[0] - exit_x) <= 1 and abs(pos[1] - exit_y) <= 1

    def generate_wind_positions(self):
        wind_positions = set()
        for pit in self.pit_positions:
            x, y = pit
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) != self.wumpus_pos and (nx, ny) != self.treasure_pos:
                    wind_positions.add((nx, ny))
        return list(wind_positions)
    
    def generate_odor_positions(self):
        odor_positions = set()
        x, y = self.wumpus_pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) != self.entry_point and (nx, ny) != self.exit_point:
                odor_positions.add((nx, ny))
        return list(odor_positions)

    def move_player(self, dx, dy):
        if self.game_over:
            return 

        new_x, new_y = self.player_pos[0] + dx, self.player_pos[1] + dy
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            self.player_pos = (new_x, new_y)
            self.check_position()
    
    def move_player_automatically(self):
        if self.path_index < len(self.path_to_exit):
            dx, dy = self.path_to_exit[self.path_index]
            self.move_player(dx, dy)
            self.path_index += 1
        else:
            print("¡El aventurero ha llegado a la salida!")

    def check_position(self):
        if self.player_pos == self.wumpus_pos:
            self.death_info = (self.player_pos, "Thanos te ha derrotado")
            print(f"Te encontraste con Thanos en las coordenadas {self.get_display_coordinates(self.player_pos)}")
            self.player_pos = self.entry_point 
        elif self.player_pos in self.pit_positions:
            self.death_info = (self.player_pos, "Caíste a un pozo")
            print(f"Caíste en un pozo en las coordenadas {self.get_display_coordinates(self.player_pos)}")
            self.player_pos = self.entry_point  
        elif self.player_pos == self.treasure_pos:
            if not self.treasure_collected:
                print(f"¡Encontraste el tesoro en las coordenadas {self.get_display_coordinates(self.player_pos)}!")
                self.treasure_collected = True
                self.treasure_pos = None  
        elif self.player_pos == self.exit_point:
            if self.treasure_collected:
                print(f"¡Escapaste con el tesoro! Has ganado el juego.")
            else:
                print(f"¡Escapaste, pero olvidaste recoger el tesoro! Has perdido el juego.")
            self.game_over = True  
        elif self.player_pos in self.wind_positions:
            print(f"¡Sientes viento en las coordenadas {self.get_display_coordinates(self.player_pos)}! ")
        elif self.player_pos in self.odor_positions:
            print(f"¡Hueles algo desagradable en las coordenadas {self.get_display_coordinates(self.player_pos)}! ")
    
    def get_display_coordinates(self, position):
        x, y = position
        letter = chr(65 + x)
        number = y + 1
        return f"{letter}{number}" 

    def draw(self):
        global TILE_SIZE  
        screen_width, screen_height = pygame.display.get_surface().get_size()
        TILE_SIZE = screen_width // self.size 
        
        for y in range(self.size):
            for x in range(self.size):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x + y) % 2 == 0:
                    pygame.draw.rect(screen, WHITE, rect)
                else:
                    pygame.draw.rect(screen, RED, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        player_rect = pygame.Rect(self.player_pos[0] * TILE_SIZE, self.player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        screen.blit(aventurero_img, player_rect.topleft)
        
        self.draw_coordinates()

        if self.game_over:
            for y in range(self.size):
                for x in range(self.size):
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if (x, y) == self.wumpus_pos:
                        screen.blit(wumpus_img, rect.topleft)
                    elif (x, y) == self.treasure_pos and not self.treasure_collected:
                        screen.blit(tesoro_img, rect.topleft)
                    elif (x, y) in self.pit_positions:
                        screen.blit(pozo_img, rect.topleft)
                    elif (x, y) in self.wind_positions:
                        screen.blit(viento_img, rect.topleft)
                    elif (x, y) in self.odor_positions:
                        screen.blit(olor_img, rect.topleft)
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_coordinates(self):
        for i in range(4):
            letter = chr(65 + i)
            text = font.render(letter, True, TEXT_COLOR)
            screen.blit(text, (i * TILE_SIZE + TILE_SIZE // 2 - text.get_width() // 2, 10))
        for i in range(4):
            text = font.render(str(i+1), True, TEXT_COLOR)
            screen.blit(text, (10, i * TILE_SIZE + TILE_SIZE // 2 - text.get_height() // 2))

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_SIZE + 100, SCREEN_SIZE + 100))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = large_font.render("Juego Terminado", True, WHITE)
        text_x = (SCREEN_SIZE + 100) // 2 - game_over_text.get_width() // 2
        text_y = (SCREEN_SIZE + 100) // 2 - game_over_text.get_height() // 2 - 50
        screen.blit(game_over_text, (text_x, text_y))

        button_width, button_height = 150, 50
        button_x = (SCREEN_SIZE + 100) // 2 - button_width // 2
        button_y = (SCREEN_SIZE + 100) // 2 + 20
        restart_button = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, RED, restart_button)

        restart_text = font.render("Menu Principal", True, WHITE)
        restart_text_x = button_x + button_width // 2 - restart_text.get_width() // 2
        restart_text_y = button_y + button_height // 2 - restart_text.get_height() // 2
        screen.blit(restart_text, (restart_text_x, restart_text_y))

        return restart_button

# Pantalla principal (menú de inicio)
def main_menu():
    screen.fill(WHITE)
    logo_img = pygame.image.load("assets/Logo.ico")
    logo_img = pygame.transform.scale(logo_img, (400, 200)) 
    screen.blit(logo_img, ((SCREEN_SIZE + 100) // 2 - 200, 50)) 
    title_text = title_font.render("EL MUNDO DE THANOS", True, BLACK)
    title_x = (SCREEN_SIZE + 100) // 2 - title_text.get_width() // 2
    title_y = 10
    screen.blit(title_text, (title_x, title_y))

    button_width, button_height = 150, 50
    start_button = pygame.Rect((SCREEN_SIZE + 100) // 2 - button_width // 2, 300, button_width, button_height)
    quit_button = pygame.Rect((SCREEN_SIZE + 100) // 2 - button_width // 2, 380, button_width, button_height)
    
    pygame.draw.rect(screen, RED, start_button)
    pygame.draw.rect(screen, RED, quit_button)

    start_text = font.render("Empezar", True, WHITE)
    quit_text = font.render("Cerrar", True, WHITE)
    
    screen.blit(start_text, (start_button.x + start_button.width // 2 - start_text.get_width() // 2, start_button.y + start_button.height // 2 - start_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.x + quit_button.width // 2 - quit_text.get_width() // 2, quit_button.y + quit_button.height // 2 - quit_text.get_height() // 2))
    
    pygame.display.flip()
    return start_button, quit_button

# Juego
wumpus_game = WumpusWorld()
running = True
in_menu = True

while running:
    clock.tick(FPS)
    
    if in_menu:
        start_button, quit_button = main_menu()
        pygame.display.flip() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if in_menu:
                if start_button.collidepoint(mouse_pos):
                    in_menu = False 
                elif quit_button.collidepoint(mouse_pos):
                    running = False
            elif wumpus_game.game_over:
                restart_button = wumpus_game.draw_game_over_screen()
                if restart_button.collidepoint(mouse_pos):
                    wumpus_game = WumpusWorld() 
                    in_menu = True  

    if not in_menu:
        wumpus_game.move_player_automatically()  # Movimiento automático
        wumpus_game.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()

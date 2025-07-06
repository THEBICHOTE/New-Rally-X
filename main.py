import pygame
import sys
import random
import math
from scripts.behavior_tree import create_enemy_behavior_tree
from scripts.pathfinding import a_star

# Inicialización de Pygame
pygame.init()
pygame.joystick.init()
pygame.mixer.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("New Rally X ")


# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
GRAY = (100, 100, 100)
LIGHT_GREEN = (100, 255, 100)
LIGHT_RED = (255, 100, 100)
DARK_GREEN = (0, 100, 0)
DARK_RED = (150, 0, 0)
PURPLE = (180, 70, 220)
ORANGE = (255, 150, 50)
CYAN = (0, 200, 200)
PINK = (255, 150, 200)

# Fuentes
FONT_LARGE = pygame.font.SysFont("arial", 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont("arial", 36)
FONT_SMALL = pygame.font.SysFont("arial", 24)

# Inicializar joysticks si están disponibles
joysticks = []
if pygame.joystick.get_count() > 0:
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)

# TAMAÑOS MODIFICADOS DE CARROS
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 36
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 36

# Configuración de música y sonidos
MUSIC_VOLUME = 0.6
SOUND_VOLUME = 0.7
sound_manager =()
music_enabled = False

# Intentar cargar música y sonidos
try:
    # Cargar música de fondo
    pygame.mixer.music.load("assets/music/background_music_1.mp3")
    
    # Lista de músicas de fondo
    background_music = [
        "assets/music/background_music_1.mp3",
        "assets/music/background_music_2.mp3",
        "assets/music/background_music_3.mp3"
    ]
    
    # Cargar efectos de sonido con el gestor
    sound_manager.load_sound("flag", "assets/sound/flag_collected.mp3", SOUND_VOLUME)
    sound_manager.load_sound("smoke", "assets/sound/smoke_released.mp3", SOUND_VOLUME)
    sound_manager.load_sound("crash", "assets/sound/crash.mp3", SOUND_VOLUME)
    sound_manager.load_sound("game_over", "assets/sound/game_over.mp3", SOUND_VOLUME)
    sound_manager.load_sound("level_complete", "assets/sound/level_complete.mp3", SOUND_VOLUME)
    sound_manager.load_sound("menu_select", "assets/sound/menu_select.mp3", SOUND_VOLUME)
    
    current_music_index = 0
    music_enabled = True
    
    # Reproducir música inicial si está disponible
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
except Exception as e:
    print(f"Advertencia: Error cargando archivos de sonido - {e}")
    print("El juego continuará sin audio.")
    music_enabled = False
    
    # Reproducir música inicial si está disponible
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
except Exception as e:
    print(f"Advertencia: Error cargando archivos de sonido - {e}")
    print("El juego continuará sin audio.")
    music_enabled = False
    
# Clase para el auto del jugador
class PlayerCar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = 3.9
        self.direction = 0
        self.smoke_cooldown = 0
        self.flags_collected = 0
        self.lives = 3
        self.invincible = 0
        self.score = 0
    
    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Verificar colisión con paredes
        if not maze.is_wall(new_x - self.width//2, new_y - self.height//2) and \
           not maze.is_wall(new_x + self.width//2, new_y - self.height//2) and \
           not maze.is_wall(new_x - self.width//2, new_y + self.height//2) and \
           not maze.is_wall(new_x + self.width//2, new_y + self.height//2):
            self.x = new_x
            self.y = new_y
            
            # Actualizar dirección
            if dx > 0: self.direction = 1
            elif dx < 0: self.direction = 3
            elif dy > 0: self.direction = 2
            elif dy < 0: self.direction = 0
    
    def use_smoke(self, smoke_list):
        if self.smoke_cooldown <= 0:
            smoke_list.append(Smoke(self.x, self.y, self.direction))
            self.smoke_cooldown = 60
            
    def draw(self, screen):
        # Determinar color basado en invencibilidad
        color = GREEN if self.invincible <= 0 or self.invincible % 6 < 3 else LIGHT_GREEN
        car_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        
        # Dibujar cuerpo del auto
        pygame.draw.rect(screen, color, car_rect, border_radius=6)
        pygame.draw.rect(screen, BLUE, 
                         (self.x - self.width//4, self.y - self.height//4, 
                          self.width//2, self.height//2), border_radius=4)
        
        # Dibujar luces según la dirección
        light_offset = 3
        if self.direction == 0:  # Arriba
            pygame.draw.circle(screen, YELLOW, (self.x - self.width//3, self.y - self.height//2 - light_offset), 5)
            pygame.draw.circle(screen, YELLOW, (self.x + self.width//3, self.y - self.height//2 - light_offset), 5)
            pygame.draw.circle(screen, RED, (self.x - self.width//3, self.y + self.height//2 + light_offset), 5)
            pygame.draw.circle(screen, RED, (self.x + self.width//3, self.y + self.height//2 + light_offset), 5)
        elif self.direction == 2:  # Abajo
            pygame.draw.circle(screen, RED, (self.x - self.width//3, self.y - self.height//2 - light_offset), 5)
            pygame.draw.circle(screen, RED, (self.x + self.width//3, self.y - self.height//2 - light_offset), 5)
            pygame.draw.circle(screen, YELLOW, (self.x - self.width//3, self.y + self.height//2 + light_offset), 5)
            pygame.draw.circle(screen, YELLOW, (self.x + self.width//3, self.y + self.height//2 + light_offset), 5)
        elif self.direction == 1:  # Derecha
            pygame.draw.circle(screen, YELLOW, (self.x + self.width//2 + light_offset, self.y - self.height//3), 5)
            pygame.draw.circle(screen, YELLOW, (self.x + self.width//2 + light_offset, self.y + self.height//3), 5)
            pygame.draw.circle(screen, RED, (self.x - self.width//2 - light_offset, self.y - self.height//3), 5)
            pygame.draw.circle(screen, RED, (self.x - self.width//2 - light_offset, self.y + self.height//3), 5)
        else:  # Izquierda
            pygame.draw.circle(screen, RED, (self.x + self.width//2 + light_offset, self.y - self.height//3), 5)
            pygame.draw.circle(screen, RED, (self.x + self.width//2 + light_offset, self.y + self.height//3), 5)
            pygame.draw.circle(screen, YELLOW, (self.x - self.width//2 - light_offset, self.y - self.height//3), 5)
            pygame.draw.circle(screen, YELLOW, (self.x - self.width//2 - light_offset, self.y + self.height//3), 5)
        
        # Dibujar indicador de dirección
        direction_length = 12
        if self.direction == 0:
            pygame.draw.line(screen, BLACK, (self.x, self.y - self.height//2), 
                            (self.x, self.y - self.height//2 - direction_length), 3)
        elif self.direction == 1:
            pygame.draw.line(screen, BLACK, (self.x + self.width//2, self.y), 
                            (self.x + self.width//2 + direction_length, self.y), 3)
        elif self.direction == 2:
            pygame.draw.line(screen, BLACK, (self.x, self.y + self.height//2), 
                            (self.x, self.y + self.height//2 + direction_length), 3)
        else:
            pygame.draw.line(screen, BLACK, (self.x - self.width//2, self.y), 
                            (self.x - self.width//2 - direction_length, self.y), 3)

# Clase para los autos enemigos
class EnemyCar:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.speed = 2.4
        self.color = color
        self.direction = 0
        self.stunned = 0
        self.path = []
        self.target_x = 0
        self.target_y = 0
        self.behavior_tree = create_enemy_behavior_tree()
    
    def update(self, game):
        if self.stunned > 0:
            self.stunned -= 1
            return
            
        # Ejecutar el árbol de comportamiento para toma de decisiones
        self.behavior_tree.execute(self, game)
        
        # Verificar colisión con humo
        for smoke in game.smoke_list:
            dx = self.x - smoke.x
            dy = self.y - smoke.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 35:
                self.stunned = 90
                return
    
    def find_path(self, maze):
        self.path = a_star((self.x, self.y), (self.target_x, self.target_y), maze)
    
    def draw(self, screen):
        color = self.color if self.stunned <= 0 else LIGHT_RED
        car_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        
        # Dibujar cuerpo del enemigo
        pygame.draw.rect(screen, color, car_rect, border_radius=6)
        pygame.draw.rect(screen, DARK_RED if self.stunned <= 0 else RED, 
                         (self.x - self.width//4, self.y - self.height//4, 
                          self.width//2, self.height//2), border_radius=4)
        
        # Dibujar luces traseras
        light_offset = 3
        if self.direction == 0:  # Arriba
            pygame.draw.circle(screen, RED, (self.x - self.width//3, self.y + self.height//2 + light_offset), 5)
            pygame.draw.circle(screen, RED, (self.x + self.width//3, self.y + self.height//2 + light_offset), 5)
        elif self.direction == 2:  # Abajo
            pygame.draw.circle(screen, RED, (self.x - self.width//3, self.y - self.height//2 - light_offset), 5)
            pygame.draw.circle(screen, RED, (self.x + self.width//3, self.y - self.height//2 - light_offset), 5)
        elif self.direction == 1:  # Derecha
            pygame.draw.circle(screen, RED, (self.x - self.width//2 - light_offset, self.y - self.height//3), 5)
            pygame.draw.circle(screen, RED, (self.x - self.width//2 - light_offset, self.y + self.height//3), 5)
        else:  # Izquierda
            pygame.draw.circle(screen, RED, (self.x + self.width//2 + light_offset, self.y - self.height//3), 5)
            pygame.draw.circle(screen, RED, (self.x + self.width//2 + light_offset, self.y + self.height//3), 5)

# Clase para las banderas
class Flag:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
    
    def draw(self, screen):
        if not self.collected:
            # Dibujar asta de bandera
            pygame.draw.rect(screen, (150, 75, 0), (self.x - 2, self.y - 15, 4, 20))
            # Dibujar bandera
            flag_points = [
                (self.x, self.y - 15),
                (self.x + 15, self.y - 10),
                (self.x, self.y - 5)
            ]
            pygame.draw.polygon(screen, RED, flag_points)

# Clase para el humo
class Smoke:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.lifetime = 90
        self.particles = []
        
        # Crear partículas iniciales
        for _ in range(25):
            self.particles.append({
                'x': x,
                'y': y,
                'dx': random.uniform(-1.5, 1.5),
                'dy': random.uniform(-1.5, 1.5),
                'size': random.randint(7, 20),
                'life': self.lifetime
            })
    
    def update(self):
        self.lifetime -= 1
        
        # Actualizar partículas existentes
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
        
        # Eliminar partículas muertas
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Agregar nuevas partículas
        if self.lifetime > 0 and random.random() < 0.4:
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': random.uniform(-1.5, 1.5),
                'dy': random.uniform(-1.5, 1.5),
                'size': random.randint(7, 20),
                'life': random.randint(40, 100)
            })
        
        return self.lifetime > 0 or len(self.particles) > 0
    
    def draw(self, screen):
        for p in self.particles:
            alpha = min(255, p['life'] * 3)
            size = p['size'] * (p['life'] / 90)
            
            # Crear superficie transparente para la partícula
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 220, 220, alpha), (size, size), size)
            screen.blit(s, (p['x'] - size, p['y'] - size))

# Clase para el laberinto
class Maze:
    def __init__(self, level):
        self.cell_size = 45
        self.cols = WIDTH // self.cell_size
        self.rows = HEIGHT // self.cell_size
        self.grid = self.generate_maze(level)
    
    def generate_maze(self, level):
        # Crear una cuadrícula vacía
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Crear bordes
        for i in range(self.rows):
            grid[i][0] = 1
            grid[i][self.cols-1] = 1
        for j in range(self.cols):
            grid[0][j] = 1
            grid[self.rows-1][j] = 1
        
        # Agregar obstáculos según el nivel
        obstacle_count = 25 + level * 4
        
        for _ in range(obstacle_count):
            i = random.randint(1, self.rows-2)
            j = random.randint(1, self.cols-2)
            
            if grid[i][j] == 0:
                free_neighbors = 0
                for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.rows and 0 <= nj < self.cols and grid[ni][nj] == 0:
                        free_neighbors += 1
                
                # Solo agregar obstáculo si tiene suficientes vecinos libres
                if free_neighbors >= 2:
                    grid[i][j] = 1
        
        return grid
    
    def is_wall(self, x, y):
        # Convertir coordenadas a celdas de la cuadrícula
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        
        # Verificar si es una pared
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 1
        return True
    
    def draw(self, screen):
        # Dibujar paredes
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 1:
                    rect = pygame.Rect(col * self.cell_size, row * self.cell_size, 
                                      self.cell_size, self.cell_size)
                    pygame.draw.rect(screen, DARK_GREEN, rect)
                    pygame.draw.rect(screen, (0, 80, 0), rect, 2)
        
        # Dibujar caminos
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 0:
                    rect = pygame.Rect(col * self.cell_size, row * self.cell_size, 
                                      self.cell_size, self.cell_size)
                    pygame.draw.rect(screen, (50, 50, 50), rect)
                    pygame.draw.rect(screen, (70, 70, 70), rect, 1)

# Clase para elementos del menú
class MenuItem:
    def __init__(self, text, position, action):
        self.text = text
        self.position = position
        self.action = action
        self.font = FONT_MEDIUM
        self.selected = False
        self.rect = pygame.Rect(0, 0, 0, 0)
    
    def draw(self, screen):
        color = YELLOW if self.selected else WHITE
        text_surface = self.font.render(self.text, True, color)
        self.rect = text_surface.get_rect(center=self.position)
        screen.blit(text_surface, self.rect)
    
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

# Clase principal del juego
class Game:
    def __init__(self):
        self.level = 1
        self.state = "start_screen"
        self.player = None
        self.enemies = []
        self.flags = []
        self.smoke_list = []
        self.maze = None
        self.menu_items = []
        self.selected_item = 0
        self.start_time = 0
        self.music_paused = False
        self.initialize_menu()
        
        # Iniciar música si está disponible
        if music_enabled and background_music:
            pygame.mixer.music.load(background_music[0])
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
    
    def initialize_menu(self):
        # Crear elementos del menú principal
        self.menu_items = [
            MenuItem("Jugar", (WIDTH//2, HEIGHT//2 - 50), "start_game"),
            MenuItem("Controles", (WIDTH//2, HEIGHT//2), "show_controls"),
            MenuItem("Música: ON", (WIDTH//2, HEIGHT//2 + 50), "toggle_music"),
            MenuItem("Salir", (WIDTH//2, HEIGHT//2 + 100), "quit")
        ]
        self.menu_items[self.selected_item].selected = True
    
    def toggle_music(self):
        global music_enabled
        music_enabled = not music_enabled
        
        if music_enabled:
            self.menu_items[2].text = "Música: ON"
            if background_music:
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
        else:
            self.menu_items[2].text = "Música: OFF"
            pygame.mixer.music.stop()
        
        if music_enabled:
            sound_manager.play("menu_select")
    
    def play_next_music(self):
        if not music_enabled or not background_music:
            return
            
        # Cambiar a la siguiente canción en la lista
        current_music_index = (background_music.index(pygame.mixer.music.get_busy()) + 1) % len(background_music)
        pygame.mixer.music.load(background_music[current_music_index])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
    
    def initialize_level(self):
        # Crear laberinto para el nivel actual
        self.maze = Maze(self.level)
        
        # Posiciones seguras para el jugador
        safe_positions = [
            (WIDTH//4, HEIGHT//4),
            (3*WIDTH//4, HEIGHT//4),
            (WIDTH//4, 3*HEIGHT//4),
            (3*WIDTH//4, 3*HEIGHT//4)
        ]
        start_x, start_y = random.choice(safe_positions)
        self.player = PlayerCar(start_x, start_y)
        
        # Crear enemigos
        self.enemies = []
        enemy_colors = [RED, ORANGE, PURPLE, PINK, CYAN]
        for _ in range(min(3 + self.level // 2, 6)):
            while True:
                x = random.randint(50, WIDTH-50)
                y = random.randint(50, HEIGHT-50)
                # Asegurar que no estén en una pared y lejos del jugador
                if not self.maze.is_wall(x, y) and \
                   math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2) > 150:
                    self.enemies.append(EnemyCar(x, y, random.choice(enemy_colors)))
                    break
        
        # Crear banderas
        self.flags = []
        flag_count = 5 + self.level // 2
        for _ in range(flag_count):
            while True:
                x = random.randint(50, WIDTH-50)
                y = random.randint(50, HEIGHT-50)
                # Asegurar que no estén en una pared y lejos del jugador
                if not self.maze.is_wall(x, y) and \
                   math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2) > 100:
                    self.flags.append(Flag(x, y))
                    break
    
    def update(self):
        if self.state != "playing":
            return
        
        # Actualizar tiempos de enfriamiento
        if self.player.smoke_cooldown > 0:
            self.player.smoke_cooldown -= 1
        if self.player.invincible > 0:
            self.player.invincible -= 1
        
        # Actualizar humo
        self.smoke_list = [smoke for smoke in self.smoke_list if smoke.update()]
        
        # Actualizar enemigos
        for enemy in self.enemies:
            enemy.update(self)
            
            # Verificar colisión con jugador
            if self.player.invincible <= 0:
                dx = self.player.x - enemy.x
                dy = self.player.y - enemy.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < (self.player.width * 0.7 + enemy.width * 0.7):
                    self.player.lives -= 1
                    self.player.invincible = 90
                    
                    if music_enabled:
                        sound_manager.play("crash")
                    if self.player.lives <= 0:
                        self.state = "game_over"
                        if music_enabled:
                             sound_manager.play("game_over")
                        return
        
        # Recolectar banderas
        for flag in self.flags:
            if not flag.collected:
                dx = self.player.x - flag.x
                dy = self.player.y - flag.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < (self.player.width + flag.width) // 2:
                    flag.collected = True
                    self.player.flags_collected += 1
                    self.player.score += 100
                    
                    if music_enabled:
                        sound_manager.play("flag")
        
        # Verificar si se recolectaron todas las banderas
        if all(flag.collected for flag in self.flags):
            self.player.score += 500 * self.level
            self.state = "level_complete"
            if music_enabled:
                sound_manager.play("level_complete")
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Dibujar diferentes pantallas según el estado del juego
        if self.state == "start_screen":
            self.draw_start_screen(screen)
            return
        elif self.state == "menu":
            self.draw_menu(screen)
            return
        elif self.state == "controls":
            self.draw_controls_screen(screen)
            return
        elif self.state == "paused":
            # Dibujar juego en pausa
            self.maze.draw(screen)
            for smoke in self.smoke_list:
                smoke.draw(screen)
            for flag in self.flags:
                flag.draw(screen)
            for enemy in self.enemies:
                enemy.draw(screen)
            self.player.draw(screen)
            self.draw_hud(screen)
            self.draw_pause_screen(screen)
            return
        
        # Dibujar juego principal
        self.maze.draw(screen)
        for smoke in self.smoke_list:
            smoke.draw(screen)
        for flag in self.flags:
            flag.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        self.player.draw(screen)
        self.draw_hud(screen)
        
        # Dibujar pantallas de estado
        if self.state == "game_over":
            self.draw_game_over(screen)
        elif self.state == "level_complete":
            self.draw_level_complete(screen)
    
    def draw_hud(self, screen):
        # Dibujar barra superior de información
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, 40))
        pygame.draw.line(screen, (100, 100, 100), (0, 40), (WIDTH, 40), 2)
        
        # Mostrar puntaje
        score_text = FONT_SMALL.render(f"Puntos: {self.player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Mostrar vidas
        lives_text = FONT_SMALL.render(f"Vidas: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (WIDTH - 120, 10))
        
        # Mostrar nivel
        level_text = FONT_SMALL.render(f"Nivel: {self.level}", True, WHITE)
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 10))
        
        # Mostrar banderas recolectadas
        flags_text = FONT_SMALL.render(
            f"Banderas: {self.player.flags_collected}/{len(self.flags)}", 
            True, YELLOW
        )
        screen.blit(flags_text, (WIDTH - 300, 10))
        
        # Mostrar cooldown del humo
        if self.player.smoke_cooldown > 0:
            pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 500, 10, 100, 20))
            pygame.draw.rect(screen, BLUE, (WIDTH - 500, 10, 100 * (1 - self.player.smoke_cooldown/60), 20))
            smoke_text = FONT_SMALL.render("Humo", True, WHITE)
            screen.blit(smoke_text, (WIDTH - 500, 10))
        
        # Mostrar controles de música
        music_text = FONT_SMALL.render("M: Música", True, CYAN)
        screen.blit(music_text, (WIDTH - 150, HEIGHT - 30))
        
        next_music_text = FONT_SMALL.render("N: Siguiente canción", True, CYAN)
        screen.blit(next_music_text, (20, HEIGHT - 30))
    
    def draw_start_screen(self, screen):
        # Fondo animado
        t = pygame.time.get_ticks() / 1000
        for i in range(20):
            for j in range(15):
                x = i * 40
                y = j * 40
                color_val = 50 + 50 * math.sin(t + i * 0.2 + j * 0.1)
                pygame.draw.rect(screen, (0, color_val, 0), (x, y, 40, 40))
        
        # Título del juego
        title = FONT_LARGE.render("NEW RALLY X", True, YELLOW)
        title_shadow = FONT_LARGE.render("NEW RALLY X", True, (100, 100, 0))
        screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 103))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Texto parpadeante
        if int(t * 2) % 2 == 0:
            start_text = FONT_MEDIUM.render("Presiona cualquier botón para continuar", True, WHITE)
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 450))
        
        # Controles
        controls_text = FONT_SMALL.render("Controles: Flechas/Joystick para mover, ESPACIO/A para humo, P/START para pausa", True, CYAN)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, 520))
        
        music_controls = FONT_SMALL.render("M: Alternar música, N: Siguiente canción, +-: Volumen", True, BLUE)
        screen.blit(music_controls, (WIDTH//2 - music_controls.get_width()//2, 560))
    
    def draw_menu(self, screen):
        # Fondo animado
        t = pygame.time.get_ticks() / 1000
        for i in range(20):
            for j in range(15):
                x = i * 40
                y = j * 40
                color_val = 30 + 30 * math.sin(t + i * 0.2 + j * 0.1)
                pygame.draw.rect(screen, (0, color_val, 0), (x, y, 40, 40))
        
        # Título
        title = FONT_LARGE.render("NEW RALLY X", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Elementos del menú
        for item in self.menu_items:
            item.draw(screen)
        
        # Información de joystick
        if joysticks:
            joy_text = FONT_SMALL.render(f"Joystick conectado: {joysticks[0].get_name()}", True, GREEN)
            screen.blit(joy_text, (20, HEIGHT - 30))
        
        # Instrucciones de navegación
        nav_text = FONT_SMALL.render("Usa las flechas o joystick para navegar, ENTER/A para seleccionar", True, CYAN)
        screen.blit(nav_text, (WIDTH//2 - nav_text.get_width()//2, HEIGHT - 50))
    
    def draw_controls_screen(self, screen):
        screen.fill((0, 20, 0))
        
        # Título
        title = FONT_LARGE.render("CONTROLES", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        # Controles de teclado
        key_texts = [
            "Teclado:",
            "Flechas - Mover el auto",
            "ESPACIO - Soltar humo",
            "P - Pausa",
            "ESC - Volver al menú",
            "M - Alternar música",
            "N - Siguiente canción",
            "+/- - Ajustar volumen"
        ]
        
        for i, text in enumerate(key_texts):
            text_surf = FONT_MEDIUM.render(text, True, WHITE)
            screen.blit(text_surf, (WIDTH//4 - text_surf.get_width()//2, 150 + i * 40))
        
        # Controles de joystick
        if joysticks:
            joy_texts = [
                "Joystick:",
                "Analógico izquierdo/D-Pad - Mover",
                "Botón A - Soltar humo",
                "Botón START - Pausa",
                "Botón B - Volver al menú",
                "Botón X - Alternar música",
                "Botón Y - Siguiente canción",
                "Gatillos - Ajustar volumen"
            ]
            
            for i, text in enumerate(joy_texts):
                text_surf = FONT_MEDIUM.render(text, True, CYAN)
                screen.blit(text_surf, (3*WIDTH//4 - text_surf.get_width()//2, 150 + i * 40))
        else:
            no_joy = FONT_MEDIUM.render("No se detectó joystick", True, RED)
            screen.blit(no_joy, (3*WIDTH//4 - no_joy.get_width()//2, 230))
        
        # Instrucción para volver
        back_text = FONT_MEDIUM.render("Presiona ESC o B para volver al menú", True, GREEN)
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, 480))
    
    def draw_pause_screen(self, screen):
        # Capa semitransparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        title = FONT_LARGE.render("JUEGO EN PAUSA", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        continue_text = FONT_MEDIUM.render("Presiona P o START para continuar", True, WHITE)
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, 250))
        
        menu_text = FONT_MEDIUM.render("Presiona ESC o B para volver al menú", True, WHITE)
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, 300))
        
        music_text = FONT_MEDIUM.render(f"Música: {'ON' if music_enabled else 'OFF'}", True, CYAN)
        screen.blit(music_text, (WIDTH//2 - music_text.get_width()//2, 350))
    
    def draw_game_over(self, screen):
        # Capa semitransparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Texto de game over
        title = FONT_LARGE.render("¡GAME OVER!", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        # Estadísticas
        score_text = FONT_MEDIUM.render(f"Puntuación final: {self.player.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 250))
        
        level_text = FONT_MEDIUM.render(f"Nivel alcanzado: {self.level}", True, YELLOW)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 300))
        
        # Opciones
        restart_text = FONT_MEDIUM.render("Presiona R o A para reiniciar", True, GREEN)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 400))
        
        menu_text = FONT_MEDIUM.render("Presiona ESC o B para volver al menú", True, WHITE)
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, 450))
    
    def draw_level_complete(self, screen):
        # Capa semitransparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Texto de nivel completado
        title = FONT_LARGE.render("¡NIVEL COMPLETADO!", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        # Puntos obtenidos
        score_text = FONT_MEDIUM.render(f"Puntos obtenidos: {500 * self.level}", True, YELLOW)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 250))
        
        total_text = FONT_MEDIUM.render(f"Puntuación total: {self.player.score}", True, YELLOW)
        screen.blit(total_text, (WIDTH//2 - total_text.get_width()//2, 300))
        
        # Opciones
        next_text = FONT_MEDIUM.render("Presiona ESPACIO o A para el siguiente nivel", True, GREEN)
        screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, 400))
        
        menu_text = FONT_MEDIUM.render("Presiona ESC o B para volver al menú", True, WHITE)
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, 450))

# Función principal del juego
def main():
    clock = pygame.time.Clock()
    game = Game()
    
    # Configuración para joystick
    joystick_deadzone = 0.5
    last_joystick_move_time = 0
    joystick_move_delay = 200
    
    # Cambio automático de música
    last_music_change = pygame.time.get_ticks()
    music_change_delay = 180000  # 3 minutos
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Cambiar música automáticamente cada 3 minutos
        if music_enabled and background_music and current_time - last_music_change > music_change_delay:
            game.play_next_music()
            last_music_change = current_time
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Manejo de botones del joystick
            if event.type == pygame.JOYBUTTONDOWN:
                handle_joystick_button(event.button, game, running)
            
            # Manejo de teclado
            if event.type == pygame.KEYDOWN:
                handle_keyboard(event.key, game, running)
        
        # Manejo de joystick en menú
        handle_joystick_menu(game, joysticks, current_time)
        
        # Movimiento del jugador
        if game.state == "playing":
            handle_player_movement(game)
        
        # Actualizar estado del juego
        game.update()
        
        # Dibujar todo
        game.draw(screen)
        
        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

# Funciones auxiliares para manejo de eventos
def handle_joystick_button(button, game, running):
    if game.state == "start_screen":
        game.state = "menu"
    elif game.state == "controls" and button == 1:  # Botón B
        game.state = "menu"
    elif game.state == "menu":
        if button == 0:  # Botón A
            handle_menu_selection(game, running)
    elif game.state == "playing":
        if button == 0:  # Botón A
            game.player.use_smoke(game.smoke_list)
        elif button == 7:  # Botón START
            game.state = "paused"
        elif button == 2:  # Botón X
            game.toggle_music()
        elif button == 3:  # Botón Y
            if music_enabled:
                game.play_next_music()
    elif game.state == "paused":
        if button == 0:  # Botón A
            game.state = "playing"
        elif button == 1:  # Botón B
            game.state = "menu"
        elif button == 2:  # Botón X
            game.toggle_music()
    elif game.state == "game_over":
        if button == 0:  # Botón A
            game.state = "playing"
            game.initialize_level()
        elif button == 1:  # Botón B
            game.state = "menu"
    elif game.state == "level_complete":
        if button == 0:  # Botón A
            game.level += 1
            game.initialize_level()
            game.state = "playing"
        elif button == 1:  # Botón B
            game.state = "menu"

def handle_keyboard(key, game, running):
    if game.state == "start_screen":
        game.state = "menu"
    elif game.state == "controls" and key == pygame.K_ESCAPE:
        game.state = "menu"
    elif game.state == "menu":
        if key == pygame.K_UP:
            navigate_menu(game, -1)
        elif key == pygame.K_DOWN:
            navigate_menu(game, 1)
        elif key == pygame.K_RETURN:
            handle_menu_selection(game, running)
        elif key == pygame.K_ESCAPE:
            running = False
    elif game.state == "playing":
        if key == pygame.K_SPACE:
            game.player.use_smoke(game.smoke_list)
        elif key == pygame.K_p:
            game.state = "paused"
        elif key == pygame.K_ESCAPE:
            game.state = "menu"
        elif key == pygame.K_m:
            game.toggle_music()
        elif key == pygame.K_n:
            if music_enabled:
                game.play_next_music()
        elif key in (pygame.K_PLUS, pygame.K_EQUALS):
            new_vol = min(1.0, pygame.mixer.music.get_volume() + 0.1)
            pygame.mixer.music.set_volume(new_vol)
        elif key == pygame.K_MINUS:
            new_vol = max(0.0, pygame.mixer.music.get_volume() - 0.1)
            pygame.mixer.music.set_volume(new_vol)
    elif game.state == "paused":
        if key in (pygame.K_p, pygame.K_RETURN):
            game.state = "playing"
        elif key == pygame.K_ESCAPE:
            game.state = "menu"
        elif key == pygame.K_m:
            game.toggle_music()
    elif game.state == "game_over":
        if key == pygame.K_r:
            game.state = "playing"
            game.initialize_level()
        elif key == pygame.K_ESCAPE:
            game.state = "menu"
    elif game.state == "level_complete":
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            game.level += 1
            game.initialize_level()
            game.state = "playing"
        elif key == pygame.K_ESCAPE:
            game.state = "menu"

def handle_menu_selection(game, running):
    if game.menu_items[game.selected_item].action == "start_game":
        game.state = "playing"
        game.initialize_level()
    elif game.menu_items[game.selected_item].action == "show_controls":
        game.state = "controls"
    elif game.menu_items[game.selected_item].action == "toggle_music":
        game.toggle_music()
    elif game.menu_items[game.selected_item].action == "quit":
        running = False

def navigate_menu(game, direction):
    game.menu_items[game.selected_item].selected = False
    game.selected_item = (game.selected_item + direction) % len(game.menu_items)
    game.menu_items[game.selected_item].selected = True

def handle_joystick_menu(game, joysticks, current_time):
    if game.state == "menu" and joysticks:
        joystick = joysticks[0]
        y_axis = joystick.get_axis(1)
        
        # Manejar navegación en menú
        if abs(y_axis) > 0.5:
            if current_time - last_joystick_move_time > 200:
                if y_axis < 0:
                    navigate_menu(game, -1)
                else:
                    navigate_menu(game, 1)
                last_joystick_move_time = current_time
        
        # Ajustar volumen con gatillos
        left_trigger = (joystick.get_axis(4) + 1) / 2
        right_trigger = (joystick.get_axis(5) + 1) / 2
        
        if left_trigger > 0.1:
            new_vol = max(0.0, pygame.mixer.music.get_volume() - 0.01)
            pygame.mixer.music.set_volume(new_vol)
        elif right_trigger > 0.1:
            new_vol = min(1.0, pygame.mixer.music.get_volume() + 0.01)
            pygame.mixer.music.set_volume(new_vol)

def handle_player_movement(game):
    dx, dy = 0, 0
    
    # Movimiento con teclado
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        dy = -game.player.speed
    if keys[pygame.K_DOWN]:
        dy = game.player.speed
    if keys[pygame.K_LEFT]:
        dx = -game.player.speed
    if keys[pygame.K_RIGHT]:
        dx = game.player.speed
    
    # Movimiento con joystick
    if joysticks:
        joystick = joysticks[0]
        x_axis = joystick.get_axis(0)
        y_axis = joystick.get_axis(1)
        
        if abs(x_axis) > 0.1:
            dx = x_axis * game.player.speed
        if abs(y_axis) > 0.1:
            dy = y_axis * game.player.speed
        
        # Movimiento con D-Pad
        hat = joystick.get_hat(0)
        dx += hat[0] * game.player.speed
        dy += hat[1] * game.player.speed
    
    # Mover al jugador
    game.player.move(dx, dy, game.maze)

if __name__ == "__main__":
    main()  
#Wilbel Benitez
#22-SISN-2-064
import random

class Node:
    #Nodo base del árbol de comportamiento"""
    def execute(self, enemy, game):
        return True

class Sequence(Node):
   #Ejecuta nodos en secuencia hasta que uno falle"""
    def __init__(self, nodes):
        self.nodes = nodes
    
    def execute(self, enemy, game):
        for node in self.nodes:
            if not node.execute(enemy, game):
                return False
        return True

class Selector(Node):
    #Ejecuta nodos hasta que uno tenga éxito
    def __init__(self, nodes):
        self.nodes = nodes
    
    def execute(self, enemy, game):
        for node in self.nodes:
            if node.execute(enemy, game):
                return True
        return False

class Condition(Node):
    #Condición base
    def __init__(self, func):
        self.func = func
    
    def execute(self, enemy, game):
        return self.func(enemy, game)

class Action(Node):
    #Acción base
    def __init__(self, func):
        self.func = func
    
    def execute(self, enemy, game):
        return self.func(enemy, game)

def create_enemy_behavior_tree():
    #Crea el árbol de comportamiento para los enemigos
    
    # Condiciones
    def is_player_visible(enemy, game):
       #Verifica si el jugador está visible
        # Calcular distancia al jugador
        dx = enemy.x - game.player.x
        dy = enemy.y - game.player.y
        dist_sq = dx*dx + dy*dy
        
        # Si está muy cerca, siempre visible
        if dist_sq < 10000:  # 100^2
            return True
        
        # Si está demasiado lejos, no visible
        if dist_sq > 4000000:  # 2000^2
            return False
        
        # Verificar línea de visión
        steps = int(dist_sq**0.5) // 20  # Cada 20 píxeles
        if steps < 2:
            return True
            
        step_x = dx / steps
        step_y = dy / steps
        
        # Verificar cada punto intermedio
        for i in range(1, steps):
            check_x = enemy.x - i*step_x
            check_y = enemy.y - i*step_y
            if game.maze.is_wall(check_x, check_y):
                return False
                
        return True
    
    def is_player_near(enemy, game):
       #Verifica si el jugador está cerca
        dx = enemy.x - game.player.x
        dy = enemy.y - game.player.y
        dist = dx*dx + dy*dy
        return dist < 150000  # ~387 píxeles
    
    def has_path_to_player(enemy, game):
        #Verifica si hay un camino al jugador
        return len(enemy.path) > 0
    
    # Acciones
    def chase_player(enemy, game):
        #Perseguir al jugador
        if not enemy.path:
            return False
            
        # Obtener el siguiente punto en el camino
        next_x, next_y = enemy.path[0]
        
        # Calcular dirección hacia el punto
        dx = next_x - enemy.x
        dy = next_y - enemy.y
        dist = (dx*dx + dy*dy)**0.5
        
        # Si está cerca del punto, avanzar al siguiente
        if dist < 5:
            enemy.path.pop(0)
            if not enemy.path:
                return False
            next_x, next_y = enemy.path[0]
            dx = next_x - enemy.x
            dy = next_y - enemy.y
            dist = (dx*dx + dy*dy)**0.5
        
        # Normalizar dirección y mover
        if dist > 0:
            dx, dy = dx/dist, dy/dist
        enemy.x += dx * enemy.speed
        enemy.y += dy * enemy.speed
        
        # Actualizar dirección para dibujo
        if abs(dx) > abs(dy):
            enemy.direction = 1 if dx > 0 else 3
        else:
            enemy.direction = 2 if dy > 0 else 0
            
        return True
    
    def patrol_randomly(enemy, game):
        #Patrullar aleatoriamente
        # Si no hay camino o se llegó al destino, elegir nuevo destino
        if not enemy.path or ((enemy.x - enemy.target_x)**2 + (enemy.y - enemy.target_y)**2 < 25):
            # Buscar posición aleatoria válida
            while True:
                enemy.target_x = random.randint(50, game.maze.cols * game.maze.cell_size - 50)
                enemy.target_y = random.randint(50, game.maze.rows * game.maze.cell_size - 50)
                if not game.maze.is_wall(enemy.target_x, enemy.target_y):
                    break
            enemy.find_path(game.maze)
        
        # Seguir el camino si existe
        if enemy.path:
            return chase_player(enemy, game)
        return False
    
    def find_player_path(enemy, game):
        #Buscar camino al jugador
        enemy.target_x = game.player.x
        enemy.target_y = game.player.y
        enemy.find_path(game.maze)
        return True
    
    # Construir el árbol de comportamiento
    return Selector([
        Sequence([
            Condition(is_player_visible),
            Condition(is_player_near),
            Action(find_player_path),
            Action(chase_player)
        ]),
        Action(patrol_randomly)
    ])
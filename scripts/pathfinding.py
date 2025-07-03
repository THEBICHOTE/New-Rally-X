def heuristic(a, b):
    """Función heurística (distancia Manhattan)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, end, maze):
    """Implementación del algoritmo A* para encontrar camino"""
    
    # Convertir coordenadas a celdas
    start_cell = (int(start[0] // maze.cell_size), int(start[1] // maze.cell_size))
    end_cell = (int(end[0] // maze.cell_size), int(end[1] // maze.cell_size))
    
    # Si el destino es una pared, buscar celda adyacente válida
    if maze.grid[end_cell[1]][end_cell[0]] == 1:
        # Buscar en las 8 direcciones alrededor
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), 
                     (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for dx, dy in directions:
            nx, ny = end_cell[0] + dx, end_cell[1] + dy
            if 0 <= ny < maze.rows and 0 <= nx < maze.cols and maze.grid[ny][nx] == 0:
                end_cell = (nx, ny)
                break
    
    # Si aún es pared, devolver camino vacío
    if maze.grid[end_cell[1]][end_cell[0]] == 1:
        return []
    
    # Estructuras para el algoritmo
    open_set = [start_cell]
    came_from = {}
    
    # Costos g (distancia desde inicio)
    g_score = {start_cell: 0}
    
    # Costos f (g + heurística)
    f_score = {start_cell: heuristic(start_cell, end_cell)}
    
    while open_set:
        # Encontrar nodo con menor f_score
        current = min(open_set, key=lambda cell: f_score.get(cell, float('inf')))
        
        # Si llegamos al destino, reconstruir camino
        if current == end_cell:
            path = []
            while current in came_from:
                # Convertir a coordenadas de píxel (centro de la celda)
                pixel_x = current[0] * maze.cell_size + maze.cell_size // 2
                pixel_y = current[1] * maze.cell_size + maze.cell_size // 2
                path.append((pixel_x, pixel_y))
                current = came_from[current]
            path.reverse()
            return path
        
        open_set.remove(current)
        
        # Explorar vecinos (4 direcciones)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Saltar si está fuera de límites o es pared
            if not (0 <= neighbor[0] < maze.cols and 0 <= neighbor[1] < maze.rows):
                continue
                
            if maze.grid[neighbor[1]][neighbor[0]] == 1:
                continue
                
            # Calcular costo tentativo
            tentative_g = g_score.get(current, float('inf')) + 1
            
            # Si encontramos un mejor camino
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_cell)
                
                if neighbor not in open_set:
                    open_set.append(neighbor)
    
    # No se encontró camino
    return []
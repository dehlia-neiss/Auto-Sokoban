import random
import copy

WALL = -1
FLOOR = 0
GOAL = 1
BOX = 2
PLAYER = 3

def generate_random_level(rows=10, cols=10, num_boxes=3):
    # 1. Base grid with walls
    grid = [[FLOOR for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        grid[i][0] = grid[i][-1] = WALL
    for j in range(cols):
        grid[0][j] = grid[-1][j] = WALL

    # 2. Place goals randomly
    goals = []
    while len(goals) < num_boxes:
        y, x = random.randint(1, rows-2), random.randint(1, cols-2)
        if grid[y][x] == FLOOR:
            grid[y][x] = GOAL
            goals.append((y, x))

    # 3. Place boxes on goals
    boxes = copy.deepcopy(goals)

    # 4. Move boxes backward randomly (simulate reverse push)
    for i in range(num_boxes):
        y, x = boxes[i]
        for _ in range(random.randint(1, 3)):  # nb de mouvements de recul
            dirs = [(-1,0), (1,0), (0,-1), (0,1)]
            random.shuffle(dirs)
            for dy, dx in dirs:
                ny, nx = y + dy, x + dx
                by, bx = y - dy, x - dx
                if (1 <= ny < rows-1 and 1 <= nx < cols-1 and
                    1 <= by < rows-1 and 1 <= bx < cols-1 and
                    grid[ny][nx] == FLOOR and grid[by][bx] == FLOOR):
                    # Reculer la caisse
                    grid[y][x] = FLOOR
                    grid[by][bx] = BOX
                    boxes[i] = (by, bx)
                    y, x = by, bx
                    break

    # 5. Place player près d’une caisse
    py, px = boxes[0]
    for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        y, x = py + dy, px + dx
        if 1 <= y < rows-1 and 1 <= x < cols-1 and grid[y][x] == FLOOR:
            grid[y][x] = PLAYER
            break

    # 6. Final cleanup: replace all boxes and goals
    for y, x in goals:
        if grid[y][x] == FLOOR:
            grid[y][x] = GOAL
    for y, x in boxes:
        grid[y][x] = BOX

    return grid

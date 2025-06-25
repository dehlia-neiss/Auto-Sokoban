# solver.py
from collections import deque
import copy

def solve_sokoban(grid, player_pos, goals):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]

    def serialize(state_grid, player):
        return (
            tuple(tuple(row) for row in state_grid),
            tuple(player)
        )

    def is_win(state_grid):
        for y in range(rows):
            for x in range(cols):
                if goals[y][x] and state_grid[y][x] != 2:
                    return False
        return True

    def find_next_states(curr_grid, ppos):
        y, x = ppos
        result = []
        for dy, dx, move_name in directions:
            ny, nx = y + dy, x + dx
            if not (0 <= ny < rows and 0 <= nx < cols):
                continue

            dest = curr_grid[ny][nx]

            # Mouvement simple
            if dest in [0, 1]:  # sol ou objectif
                new_grid = copy.deepcopy(curr_grid)
                new_grid[y][x] = 1 if goals[y][x] else 0
                new_grid[ny][nx] = 3
                result.append((new_grid, [ny, nx], move_name))

            # Si on pousse une caisse
            elif dest == 2:
                ny2, nx2 = ny + dy, nx + dx
                if not (0 <= ny2 < rows and 0 <= nx2 < cols):
                    continue
                behind = curr_grid[ny2][nx2]
                if behind in [0, 1]:  # sol ou objectif
                    new_grid = copy.deepcopy(curr_grid)
                    new_grid[y][x] = 1 if goals[y][x] else 0
                    new_grid[ny][nx] = 3
                    new_grid[ny2][nx2] = 2
                    result.append((new_grid, [ny, nx], move_name))

        return result

    queue = deque()
    visited = set()
    start_state = (copy.deepcopy(grid), player_pos[:], [])
    queue.append(start_state)
    visited.add(serialize(grid, player_pos))

    while queue:
        curr_grid, ppos, path = queue.popleft()

        if is_win(curr_grid):
            return path

        for new_grid, new_ppos, move in find_next_states(curr_grid, ppos):
            state_id = serialize(new_grid, new_ppos)
            if state_id not in visited:
                visited.add(state_id)
                queue.append((new_grid, new_ppos, path + [move]))

    return None

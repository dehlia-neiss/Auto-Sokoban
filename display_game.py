import tkinter as tk
from tkinter import messagebox
import pygame
import sqlite3
import time
from solver import solve_sokoban
from random_level_generator import generate_random_level



from build_game import get_level

# === INITIALISATION MUSIQUE ===
def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load("assets/fond.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

def play_sound(effect_path):
    sound = pygame.mixer.Sound(effect_path)
    sound.set_volume(0.7)
    sound.play()

# === BASE DE DONNEES ===
def init_db():
    conn = sqlite3.connect("assets/scores.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            pseudo TEXT,
            moves INTEGER,
            duration FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_score(level, pseudo, moves, duration):
    conn = sqlite3.connect("assets/scores.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores (level, pseudo, moves, duration) VALUES (?, ?, ?, ?)",
              (level, pseudo, moves, duration))
    conn.commit()
    conn.close()

# === LANCEMENT DU JEU ===
def launch_game(level_name):
    play_music()
    init_db()

    grid = get_level(level_name)
    original_goals = [[cell == 1 for cell in row] for row in grid]
    rows, cols = len(grid), len(grid[0])

    root = tk.Tk()
    root.title("Auto Sokoban")
    root.focus_set()

    canvas = tk.Canvas(root, width=cols*50, height=rows*50, bg="white")
    canvas.pack()

    start_time = time.time()
    move_count = [0]
    undo_stack = []
    initial_grid = [row.copy() for row in grid]

    player_pos = [0, 0]
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == 3:
                player_pos = [y, x]

    def draw():
        canvas.delete("all")
        for y in range(rows):
            for x in range(cols):
                base_color = "white"
                if grid[y][x] == -1:
                    base_color = "black"     # mur
                elif grid[y][x] == 2:
                    base_color = "red"       # caisse
                elif grid[y][x] == 3:
                    base_color = "blue"      # joueur

                # Si c’est une zone verte (objectif), on la garde visible
                if original_goals[y][x]:
                    canvas.create_rectangle(x*50, y*50, x*50+50, y*50+50, fill="green")
                    if grid[y][x] in [2, 3]:  # caisse ou joueur par dessus
                        canvas.create_rectangle(x*50+5, y*50+5, x*50+45, y*50+45, fill=base_color)
                else:
                    canvas.create_rectangle(x*50, y*50, x*50+50, y*50+50, fill=base_color)

    def check_win():
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] == 2:
                    return False
        return True

    def animate_solution(moves_list, index=0):
     if index >= len(moves_list):
        return  # fin de l’animation

     move = moves_list[index]

    # move est une direction: 'Up', 'Down', 'Left', 'Right'
     directions = {
        'Up': (-1, 0),
        'Down': (1, 0),
        'Left': (0, -1),
        'Right': (0, 1)
    }
     dy, dx = directions[move]
     move_player(dy, dx)

    # appeler la prochaine étape après 300 ms (ajuste la vitesse ici)
     root.after(300, lambda: animate_solution(moves_list, index+1))

    def move_player(dy, dx):
        y, x = player_pos
        ny, nx = y + dy, x + dx

        # Check limites du tableau
        if ny < 0 or ny >= rows or nx < 0 or nx >= cols:
            return  # interdit hors map

        # Si case libre (vide ou zone jaune), déplacement simple
        if grid[ny][nx] in [0, 1]:
            undo_stack.append(([row.copy() for row in grid], player_pos.copy(), move_count[0]))
            grid[y][x] = 0
            grid[ny][nx] = 3
            player_pos[0], player_pos[1] = ny, nx
            move_count[0] += 1
            play_sound("assets/move.mp3")

        # Si il y a une caisse à pousser
        elif grid[ny][nx] == 2:
            ny2, nx2 = ny + dy, nx + dx

            # Check limites de la case derrière la caisse
            if ny2 < 0 or ny2 >= rows or nx2 < 0 or nx2 >= cols:
                return  # interdit hors map

            # Si case derrière la caisse libre
            if grid[ny2][nx2] in [0, 1]:
                undo_stack.append(([row.copy() for row in grid], player_pos.copy(), move_count[0]))
                # Si la caisse est poussée sur une zone jaune (1), la caisse disparait (c'est le but)
                if original_goals[ny2][nx2]:  # utiliser la matrice d’objectifs !
                    grid[ny2][nx2] = 1  # garde la zone comme objectif (verte), la caisse est livrée
                else:
                     grid[ny2][nx2] = 2   # pousse la caisse normalement

                grid[ny][nx] = 3  # joueur prend la place de la caisse
                grid[y][x] = 0    # ancienne position joueur vide
                player_pos[0], player_pos[1] = ny, nx
                move_count[0] += 1
                play_sound("assets/push.mp3")
            else:
                return  # impossible de pousser caisse

        else:
            return  # case bloquée, rien faire

        draw()

        if check_win():
            end_time = time.time()
            duration = end_time - start_time
            pseudo = "Dehlia"
            save_score(level_name, pseudo, move_count[0], duration)
            play_sound("assets/sfx/win.wav")
            messagebox.showinfo("Gagné !", f"Gagné en {move_count[0]} coups et {round(duration, 2)} secondes !")
            root.destroy()

    def undo():
        if undo_stack:
            prev_grid, prev_pos, prev_moves = undo_stack.pop()
            for y in range(rows):
                grid[y] = prev_grid[y].copy()
            player_pos[0], player_pos[1] = prev_pos
            move_count[0] = prev_moves
            draw()

    def reset():
        for y in range(rows):
            grid[y] = initial_grid[y].copy()
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] == 3:
                    player_pos[0], player_pos[1] = y, x
        move_count[0] = 0
        undo_stack.clear()
        draw()
    
    def start_solver():
     moves_list = solve_sokoban(grid, player_pos, original_goals)
     if not moves_list:
        messagebox.showinfo("Info", "Pas de solution trouvée.")
        return
     animate_solution(moves_list)

    def launch_random():
     rand_grid = generate_random_level()

    # Appelle launch_game mais avec une grille personnalisée
     root = tk.Tk()
     root.title("Sokoban Random")

    # Tu peux dupliquer launch_game ou l’adapter pour gérer cette grille :
     start_game_with_grid(rand_grid, root)


    def start_game_with_grid(grid, root):
     play_music()
     init_db()

     original_goals = [[cell == 1 for cell in row] for row in grid]
     rows, cols = len(grid), len(grid[0])
 
     canvas = tk.Canvas(root, width=cols*50, height=rows*50, bg="white")
     canvas.pack()

     move_count = [0]
     undo_stack = []
     initial_grid = [row.copy() for row in grid]

     player_pos = [0, 0]
     for y in range(rows):
        for x in range(cols):
            if grid[y][x] == 3:
                player_pos = [y, x]
    


    # === BOUTONS ===
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Undo", command=undo, width=10, bg="#d9d9d9").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Reset", command=reset, width=10, bg="#f2dede").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Résoudre", command=lambda: start_solver(), width=10, bg="#cce5ff").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Quitter", command=root.destroy, width=10, bg="#f5c6cb").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Niveau aléatoire", command=lambda: launch_random(), width=12, bg="#d4edda").pack(side=tk.LEFT, padx=5)


    def on_key(event):
        key = event.keysym
        if key == "Up": move_player(-1, 0)
        elif key == "Down": move_player(1, 0)
        elif key == "Left": move_player(0, -1)
        elif key == "Right": move_player(0, 1)

    root.bind_all("<Key>", on_key) 
    draw()
    root.mainloop()

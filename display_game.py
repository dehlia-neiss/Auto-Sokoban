import tkinter as tk
from tkinter import messagebox
import pygame
import sqlite3
import time

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
    rows, cols = len(grid), len(grid[0])

    root = tk.Tk()
    root.title("Auto Sokoban")

    canvas = tk.Canvas(root, width=cols*50, height=rows*50, bg="white")
    canvas.pack()

    start_time = time.time()
    move_count = [0]  # Utiliser une liste pour que ça soit modifiable dans une closure

    player_pos = [0, 0]
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == 3:
                player_pos = [y, x]

    def draw():
        canvas.delete("all")
        colors = {
            -1: "black",
            0: "white",
            1: "yellow",
            2: "brown",
            3: "blue"
        }
        for y in range(rows):
            for x in range(cols):
                color = colors.get(grid[y][x], "grey")
                canvas.create_rectangle(x*50, y*50, x*50+50, y*50+50, fill=color)

    def check_win():
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] == 2:
                    return False
        return True

    def move_player(dy, dx):
        y, x = player_pos
        ny, nx = y + dy, x + dx
        if grid[ny][nx] in [0, 1]:
            grid[y][x] = 0
            grid[ny][nx] = 3
            player_pos[0], player_pos[1] = ny, nx
            move_count[0] += 1
            play_sound("assets/move.mp3")
        elif grid[ny][nx] == 2:
            ny2, nx2 = ny + dy, nx + dx
            if grid[ny2][nx2] in [0, 1]:
                grid[y][x] = 0
                grid[ny][nx] = 3
                grid[ny2][nx2] = 2
                player_pos[0], player_pos[1] = ny, nx
                move_count[0] += 1
                play_sound("assets/push.mp3")
        draw()

        if check_win():
            end_time = time.time()
            duration = end_time - start_time
            pseudo = "Dehlia"  # Tu peux ajouter un champ input si tu veux que ce soit dynamique
            save_score(level_name, pseudo, move_count[0], duration)
            play_sound("assets/sfx/win.wav")
            messagebox.showinfo("Gagné !", f"Félicitations, tu as gagné en {move_count[0]} coups et {round(duration, 2)} secondes !")
            root.destroy()

    def on_key(event):
        key = event.keysym
        if key == "Up": move_player(-1, 0)
        elif key == "Down": move_player(1, 0)
        elif key == "Left": move_player(0, -1)
        elif key == "Right": move_player(0, 1)

    root.bind("<Key>", on_key)
    draw()
    root.mainloop()

from display_game import launch_game
import tkinter as tk

def start_menu():
    root = tk.Tk()
    root.title("Auto Sokoban - Menu")

    tk.Label(root, text="Sélectionne un niveau", font=("Arial", 14)).pack(pady=10)

    level_var = tk.StringVar(root)
    level_var.set("niveau_1")

    level_list = ["niveau_1", "niveau_2", "niveau_3", "niveau_4", "niveau_5"]
    dropdown = tk.OptionMenu(root, level_var, *level_list)
    dropdown.pack(pady=5)

    def start():
        root.destroy()
        launch_game(level_var.get())

    tk.Button(root, text="🎮 Jouer", command=start).pack(pady=10)
    tk.Button(root, text="❌ Quitter", command=root.quit).pack()

    root.mainloop()

if __name__ == "__main__":
    start_menu()

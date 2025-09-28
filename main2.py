import tkinter as tk
from tkinter import messagebox

def dire_bonjour():
    messagebox.showinfo("Bonjour", "Salut, étudiant en graphes !")

fenetre = tk.Tk()
fenetre.title("Ma première fenêtre")

bouton = tk.Button(fenetre, text="Clique-moi", command=dire_bonjour)
bouton.pack()

fenetre.mainloop()






import tkinter as tk

def dire_bonjour():
    print("Bonjour !")

# Fenêtre principale
root = tk.Tk()
root.title("Test tearoff")

# Création de la barre de menus principale
menubar = tk.Menu(root)
root.config(menu=menubar)

# 🔹 Sous-menu avec tearoff=1 (activé)
menu_avec_tearoff = tk.Menu(menubar, tearoff=1)
menu_avec_tearoff.add_command(label="Action 1", command=dire_bonjour)
menu_avec_tearoff.add_command(label="Action 2")
menubar.add_cascade(label="Avec Tearoff", menu=menu_avec_tearoff)

# 🔹 Sous-menu avec tearoff=0 (désactivé)
menu_sans_tearoff = tk.Menu(menubar, tearoff=0)
menu_sans_tearoff.add_command(label="Action A")
menu_sans_tearoff.add_command(label="Action B")
menubar.add_cascade(label="Sans Tearoff", menu=menu_sans_tearoff)

root.mainloop()
import tkinter as tk

# Création de la fenêtre principale
belis = tk.Tk()
belis.title("Interface Graphique - TP Graphes")

# Création de la barre de menu
menubar = tk.Menu(belis)

# Menu "Fichier"
fichier_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Fichier", menu=fichier_menu)

# Menu "Création"
creation_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Création", menu=creation_menu)

# Menu "Affichage"
affichage_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Affichage", menu=affichage_menu)

# Menu "Exécution"
execution_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Exécution", menu=execution_menu)

# Menu "Édition"
edition_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Édition", menu=edition_menu)

# Attacher le menu à la fenêtre principale
belis.config(menu=menubar)

# Boucle principale
belis.mainloop()

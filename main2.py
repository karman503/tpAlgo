import tkinter as tk
from tkinter import messagebox

def dire_bonjour():
    messagebox.showinfo("Bonjour", "Salut, étudiant en graphes !")

fenetre = tk.Tk()
fenetre.title("Ma première fenêtre")

bouton = tk.Button(fenetre, text="Clique-moi", command=dire_bonjour)
bouton.pack()

fenetre.mainloop()

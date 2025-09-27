import tkinter as tk


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface Graphique - TP Graphes")
        self._create_menu()

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        
        fichier_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=fichier_menu)

        
        creation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Création", menu=creation_menu)

        
        affichage_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Affichage", menu=affichage_menu)

        
        execution_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exécution", menu=execution_menu)

        
        edition_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edition_menu)

        self.root.config(menu=menubar)

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

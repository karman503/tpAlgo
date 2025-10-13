import tkinter as tk
from tkinter import Canvas, Menu, filedialog, messagebox
from tkinter import ttk
import math
from tkinter import simpledialog
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from docx import Document

afficher_etiquettes_aretes = False  # Variable d'état pour afficher les étiquettes des arêtes


# Dictionnaire pour stocker les sommets et arêtes de chaque onglet
tab_data = {}

# Variables globales pour la création
creation_sommet = False
creation_arete = False
arete_orientee = False
sommet_selectionne = None  # Sommet sélectionné pour ajouter une arête
current_file = None  # Fichier en cours
# Variables globales pour suivre l'état des arêtes
arete_orientee_creee = False
arete_non_orientee_creee = False


# Créer la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Algorithme des graphes")
fenetre.geometry("800x600")

# Créer un widget Notebook pour les onglets
notebook = ttk.Notebook(fenetre)
notebook.pack(expand=1, fill='both')

# Créer un cadre pour afficher les matrices
matrice_frame = tk.Frame(fenetre)
matrice_frame.pack(pady=10)

# Sous-cadres pour les matrices
matrice_adj_frame = tk.Frame(matrice_frame)
matrice_adj_frame.grid(row=0, column=0, padx=10)

matrice_inc_frame = tk.Frame(matrice_frame)
matrice_inc_frame.grid(row=0, column=1, padx=10)


# Fonction pour gérer le clic sur "Nouveau" (ajouter un nouvel onglet)
def nouveau():
    new_tab = tk.Frame(notebook)
    
    # Créer un frame pour contenir le canvas et la scrollbar
    canvas_frame = tk.Frame(new_tab)
    canvas_frame.pack(expand=1, fill='both')
    
    # Créer le canvas
    canvas = tk.Canvas(canvas_frame, bg='white')
    new_tab.canvas = canvas
    
    # Créer les scrollbars
    scrollbar_y = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
    scrollbar_x = tk.Scrollbar(canvas_frame, orient='horizontal', command=canvas.xview)
    
    # Configurer le canvas pour utiliser les scrollbars
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    
    # Positionner les éléments avec grid
    canvas.grid(row=0, column=0, sticky='nsew')
    scrollbar_y.grid(row=0, column=1, sticky='ns')
    scrollbar_x.grid(row=1, column=0, sticky='ew')
    
    # Configurer le redimensionnement
    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)
    
    # Binding pour le click
    canvas.bind("<Button-1>", lambda event: canvas_click(event, canvas))
    
    # Créer un cadre pour les matrices
    matrice_frame = tk.Frame(new_tab)
    matrice_frame.pack(pady=10)
    
    matrice_adj_frame = tk.Frame(matrice_frame)
    matrice_adj_frame.pack(side=tk.LEFT, padx=10)
    
    matrice_inc_frame = tk.Frame(matrice_frame)
    matrice_inc_frame.pack(side=tk.LEFT, padx=10)
    
    notebook.add(new_tab, text="Nouveau Graphe")
    notebook.select(new_tab)
    
    # Initialiser les données pour le nouvel onglet
    tab_data[str(new_tab)] = {
        'sommets': [],
        'aretes': set(),  # Utiliser un ensemble pour éviter les doublons
        'arete_orientee': False,
        'canvas': canvas,
        'matrice_adj_frame': matrice_adj_frame,
        'matrice_inc_frame': matrice_inc_frame
    }

# Variable globale pour garder la trace du nombre de sommets
sommets_count = 0

# Fonction pour Ouvrir des fichiers de differentes extension
def ouvrir_fichier():
    global current_file, sommets_count, aretes
    aretes = set()
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Tous les fichiers", "*.*"),
            ("Fichiers texte", "*.txt"),
            ("Fichiers Word", "*.docx"),
            ("Fichiers PDF", "*.pdf"),
            ("Fichiers Python", "*.py"),
        ]
    )

    if file_path:
        extension = os.path.splitext(file_path)[1].lower()
        current_file = file_path
        new_tab = tk.Frame(notebook)
        notebook.add(new_tab, text=os.path.basename(file_path))
        notebook.select(new_tab)

        try:
            # === Cas 1 : fichier .py ===
            if extension == '.py':
                with open(file_path, 'r', encoding='utf-8') as file:
                    contenu = file.read()

                namespace = {}
                exec(contenu, namespace)

                aretes = set(namespace.get('aretes', []))
                aretes_orientees = set(namespace.get('aretes_orientees', []))

                type_arete = 'orientée' if aretes_orientees else ('non orientée' if aretes else None)

                canvas = tk.Canvas(new_tab, bg='white')
                canvas.pack(expand=1, fill='both')

                tab_data[str(new_tab)] = {
                    'sommets': namespace.get('sommets', []),
                    'aretes': aretes,
                    'aretes_orientees': aretes_orientees,
                    'arete_orientee': type_arete == 'orientée',
                    'type_arete': type_arete,
                    'matrice_adj_frame': None,
                    'matrice_inc_frame': None
                }

                sommets_count = len(tab_data[str(new_tab)]['sommets'])

                dessiner_graphe(canvas, str(new_tab))

                for arete in tab_data[str(new_tab)]['aretes']:
                    if len(arete) == 2:
                        dessiner_arete(*arete, canvas)

                for arete_orientee in tab_data[str(new_tab)]['aretes_orientees']:
                    if len(arete_orientee) == 2:
                        dessiner_arete_orientee(*arete_orientee, canvas)

                reponse = messagebox.askyesno("Modifier le Graphe", "Voulez-vous modifier votre graphe ?")

                if reponse:
                    global creation_sommet, creation_arete, sommet_selectionne
                    creation_sommet = True
                    creation_arete = False
                    sommet_selectionne = None
                    canvas.bind("<Button-1>", lambda event: canvas_click(event, canvas))

                    if type_arete == 'orientée':
                        mon_menu.entryconfig("Orientée", state="normal")
                        mon_menu.entryconfig("Non-orientée", state="disabled")
                    elif type_arete == 'non orientée':
                        mon_menu.entryconfig("Non-orientée", state="normal")
                        mon_menu.entryconfig("Orientée", state="disabled")

            # === Cas 2 : fichier .txt ===
            elif extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    contenu = file.read()

                text_widget = tk.Text(new_tab, wrap='word')
                text_widget.insert('1.0', contenu)
                text_widget.config(state='disabled')
                text_widget.pack(expand=1, fill='both')

            # === Cas 3 : fichier .docx ===
            elif extension == '.docx':
                doc = Document(file_path)
                contenu = "\n".join([para.text for para in doc.paragraphs])

                text_widget = tk.Text(new_tab, wrap='word')
                text_widget.insert('1.0', contenu)
                text_widget.config(state='disabled')
                text_widget.pack(expand=1, fill='both')

            # === Cas autres (non gérés) ===
            else:
                messagebox.showwarning("Type non pris en charge", f"Le fichier '{extension}' n'est pas pris en charge pour l'ouverture dans cette application.")
                notebook.forget(new_tab)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier : {e}")

# Fonction pour enregistrer le fichier actuel
def enregistrer_fichier():
    global current_file
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)  # Convertir en chaîne pour utiliser comme clé
    if current_file:  # Si un fichier est déjà ouvert, enregistrez-le
        with open(current_file, 'w') as file:
            file.write(sauvegarder_graphe(tab_key))  # Passer la clé de chaîne
    else:
        enregistrer_sous()  # Si aucun fichier n'est ouvert, appeler enregistrer_sous

# Fonction pour enregistrer sous le fichier actuel
def enregistrer_sous():
    global current_file
    fichier = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Fichiers Python", "*.py")])
    if fichier:
        current_tab = notebook.nametowidget(notebook.select())
        tab_key = str(current_tab)  # Convertir en chaîne pour utiliser comme clé
        with open(fichier, 'w') as file:
            file.write(sauvegarder_graphe(tab_key))  # Passer la clé de chaîne
            current_file = fichier  # Mettez à jour current_file ici
            notebook.tab(notebook.select(), text=fichier.split('/')[-1])

# Fonction pour fermer l'onglet actuel
def fermer_fichier():
    global current_file
    current_tab = notebook.select()  # Obtenir l'onglet actuellement sélectionné
    if current_tab:
        tab_key = str(current_tab)
        data = tab_data.get(tab_key, {})

        # Vérifiez si 'matrice_adj_frame' existe avant d'y accéder
        if data.get('matrice_adj_frame') is not None:
            for widget in data['matrice_adj_frame'].winfo_children():
                widget.destroy()  # Détruire tous les widgets enfants de matrice_adj_frame

        # Fermer l'onglet actuel sans affecter les autres
        notebook.forget(current_tab)
        current_file = None
        messagebox.showinfo("Info", "Fichier fermé avec succès.")
    else:
        messagebox.showwarning("Avertissement", "Aucun fichier ouvert à fermer.")

# Fonction pour quitter l'application
def quitter_application():
    confirmation = messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?")
    if confirmation:
        fenetre.quit()

# Fonctions pour créer des sommets et des arêtes
def creer_sommet():
    global creation_sommet, creation_arete
    creation_sommet = True
    creation_arete = False

# Fonction pour créer une arête orientée
def creer_arete_oriente():
    global creation_sommet, creation_arete
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Vérifier si un type d'arête a déjà été créé
    if 'type_arete' in tab_data[tab_key] and tab_data[tab_key]['type_arete'] is not None and tab_data[tab_key]['type_arete'] != 'orientée':
        messagebox.showerror("Erreur", "Vous ne pouvez pas créer des arêtes orientées et non orientées dans le même onglet.")
        return

    creation_sommet = False
    creation_arete = True
    tab_data[tab_key]['arete_orientee'] = True  # Utiliser str(current_tab)
    tab_data[tab_key]['type_arete'] = 'orientée'  # Mettre à jour le type d'arête

# Fonction pour créer une arête non orientée
def creer_arete_non_oriente():
    global creation_sommet, creation_arete
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Vérifier si un type d'arête a déjà été créé
    if 'type_arete' in tab_data[tab_key] and tab_data[tab_key]['type_arete'] is not None and tab_data[tab_key]['type_arete'] != 'non orientée':
        messagebox.showerror("Erreur", "Vous ne pouvez pas créer des arêtes orientées et non orientées dans le même onglet.")
        return

    creation_sommet = False
    creation_arete = True
    tab_data[tab_key]['arete_orientee'] = False  # Utiliser str(current_tab)
    tab_data[tab_key]['type_arete'] = 'non orientée'  # Mettre à jour le type d'arête

# Dessiner le graphe
def dessiner_graphe(canvas, current_tab):
    canvas.delete("graphe")  # Efface seulement les éléments du graphe, pas les étiquettes
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']
    
    # Initialiser les dimensions max/min
    if not sommets:  # Si aucun sommet n'existe, éviter d'initialiser min/max
        return  # Sortir si aucun sommet

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')
    
    # Dessiner les arêtes
    for s1, s2, orientee in aretes:
        x1, y1 = sommets[s1]
        x2, y2 = sommets[s2]
        
        # Mettre à jour les dimensions max/min
        min_x = min(min_x, x1, x2)
        min_y = min(min_y, y1, y2)
        max_x = max(max_x, x1, x2)
        max_y = max(max_y, y1, y2)
        
        if orientee:
            draw_arrow(canvas, x1, y1, x2, y2)  # Dessine une flèche pour l'arête orientée
        else:
            canvas.create_line(x1, y1, x2, y2, tags="graphe")  # Dessine une ligne pour l'arête non orientée
        
    # Dessiner les sommets
    for i, (x, y) in enumerate(sommets):
        canvas.create_oval(x-10, y-10, x+10, y+10, fill="blue", tags="graphe")
        canvas.create_text(x, y, text=str(i+1), fill="white", tags="graphe")
        
        # Mettre à jour les dimensions max/min
        min_x = min(min_x, x-10)
        min_y = min(min_y, y-10)
        max_x = max(max_x, x+10)
        max_y = max(max_y, y+10)
    
    # Ajouter une marge autour du graphe
    margin = 50
    if sommets:  # Seulement si le graphe n'est pas vide
        scroll_region = (
            min_x - margin,
            min_y - margin,
            max_x + margin,
            max_y + margin
        )
        canvas.configure(scrollregion=scroll_region)
    
    # Mettre à jour le canvas
    canvas.update_idletasks()

# Dessiner une arête orientée (flèche)
def draw_arrow(canvas, x1, y1, x2, y2):
    # Calculer l'angle de la ligne
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Longueur et largeur de la flèche
    arrow_length = 15
    arrow_width = 5
    
    # Trouver le rayon du sommet
    rayon = 10  # Ajustez ce rayon selon la taille de vos sommets
    
    # Calculer les positions des points de départ et d'arrivée
    # Point de départ sur le sommet
    start_x = x1 + (rayon * math.cos(angle))  # Point de départ sur le sommet
    start_y = y1 + (rayon * math.sin(angle))  # Point de départ sur le sommet
    
    # Point d'arrivée sur le sommet
    end_x = x2 - (rayon * math.cos(angle))  # Point d'arrivée sur le sommet
    end_y = y2 - (rayon * math.sin(angle))  # Point d'arrivée sur le sommet
    
    # Dessiner la ligne principale
    canvas.create_line(start_x, start_y, end_x, end_y, fill="black", width=2)
    
    # Calculer les coordonnées de la tête de la flèche
    x_arrow1 = end_x - arrow_length * math.cos(angle - math.pi / 6)
    y_arrow1 = end_y - arrow_length * math.sin(angle - math.pi / 6)
    x_arrow2 = end_x - arrow_length * math.cos(angle + math.pi / 6)
    y_arrow2 = end_y - arrow_length * math.sin(angle + math.pi / 6)
    
    # Dessiner la tête de la flèche
    canvas.create_polygon(end_x, end_y, x_arrow1, y_arrow1, x_arrow2, y_arrow2, fill="black", outline="black")
    
# Fonction pour vérifier si le nouveau sommet est trop proche d'un sommet existant
def sommet_trop_proche(nouveau_sommet, sommets_existants, seuil=20):
    for sx, sy in sommets_existants:
        if math.sqrt((sx - nouveau_sommet[0]) * 2 + (sy - nouveau_sommet[1]) * 2) < seuil:
            return True
    return False

def canvas_click(event, canvas):
    global sommet_selectionne
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']
    
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    
    if creation_sommet:
        nouveau_sommet = (x, y)
        if not sommet_trop_proche(nouveau_sommet, sommets):
            sommets.append(nouveau_sommet)
            dessiner_graphe(canvas, current_tab)
        else:
            messagebox.showerror("Erreur", "Le sommet est trop proche d'un sommet existant.")
    
    elif creation_arete:
        for i, (sx, sy) in enumerate(sommets):
            if math.sqrt((sx - x) ** 2 + (sy - y) ** 2) <= 10:  # Vérifie si le clic est proche d'un sommet
                if sommet_selectionne is None:
                    sommet_selectionne = i  # Sélectionne le sommet
                else:
                    orientee = data['arete_orientee']  # Vérifie si les arêtes sont orientées
                    if orientee:
                        aretes.add((sommet_selectionne, i, True))  # Arête orientée
                    else:
                        aretes.add((sommet_selectionne, i, False))  # Arête non orientée
                    
                    dessiner_etiquette_arete(canvas, sommets, sommet_selectionne, i, len(aretes) - 1)
                    sommet_selectionne = None  # Réinitialise la sélection
                break
    
    dessiner_graphe(canvas, current_tab)
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

def dessiner_etiquette_arete(canvas, sommets, s1, s2, index):
    x1, y1 = sommets[s1]
    x2, y2 = sommets[s2]

    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    offset = 20

    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx**2 + dy**2)
    if length != 0:
        dx /= length
        dy /= length

    perp_x = -dy * offset
    perp_y = dx * offset
    label_x = mx + perp_x
    label_y = my + perp_y

    canvas.create_text(label_x, label_y, text=f"A{index+1}",
                       fill="red", font=("Arial", 10, "bold"),
                       tags="etiquette_arete")

# Sauvegarder le graphe dans un format lisible
def sauvegarder_graphe(current_tab):
    tab_key = str(current_tab)
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    graphe_data = f"sommets = {sommets}\naretes = {list(aretes)}\n"
    return graphe_data

# Fonction pour vérifier si un sommet est trop proche d'un autre
def sommet_trop_proche(nouveau_sommet, sommets):
    x, y = nouveau_sommet
    for sx, sy in sommets:
        if math.sqrt((sx - x)**2 + (sy - y)**2) <= 20:  # Seuil de proximité
            return True
    return False

# Fonction pour dessiner le graphe
def dessiner_graphe(canvas, current_tab):
    canvas.delete("all")
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']
    
    # Dessiner les arêtes d'abord
    for index, (s1, s2, orientee) in enumerate(aretes):
        x1, y1 = sommets[s1]
        x2, y2 = sommets[s2]
        
        if orientee:
            draw_arrow(canvas, x1, y1, x2, y2)
        else:
            canvas.create_line(x1, y1, x2, y2, width=2, tags="arete")
        
        dessiner_etiquette_arete(canvas, sommets, s1, s2, index)
    
    # Dessiner les sommets par-dessus
    for i, (x, y) in enumerate(sommets):
        canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="blue", tags="sommet")
        canvas.create_text(x, y, text=str(i+1), fill="white", font=("Arial", 10, "bold"))


def afficher_graphe_networkx():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data.get(str(current_tab))
    
    if not data:
        messagebox.showerror("Erreur", "Aucune donnée disponible pour cet onglet.")
        return

    sommets = data['sommets']
    aretes = data['aretes']
    orientee = data['arete_orientee']

    if not sommets:
        messagebox.showinfo("Info", "Le graphe est vide.")
        return

    # Construire le graphe avec NetworkX
    G = nx.DiGraph() if orientee else nx.Graph()

    for i in range(len(sommets)):
        G.add_node(i)

    for s1, s2, _ in aretes:
        G.add_edge(s1, s2)

    # Utiliser les vraies positions cliquées pour le dessin
    pos = {i: (x, -y) for i, (x, y) in enumerate(sommets)}

    # Numérotation des sommets à partir de 1
    labels = {i: str(i + 1) for i in G.nodes()}

    # Créer la nouvelle fenêtre
    fenetre_graphe = tk.Toplevel()
    fenetre_graphe.title("Affichage du Graphe")

    fig, ax = plt.subplots(figsize=(6, 5))

    # Dessiner le graphe avec pos et labels
    nx.draw(
        G, pos, labels=labels,
        node_color='orange',      # couleur des sommets
        edge_color='black',       # couleur des arêtes
        node_size=700,            # taille des sommets
        width=2.5,                # épaisseur des arêtes
        font_weight='bold', ax=ax
    )

    # Intégrer matplotlib dans Tkinter
    canvas = FigureCanvasTkAgg(fig, master=fenetre_graphe)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Fonction pour générer la matrice d'incidence
def generer_matrice_incidence():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = list(data['aretes'])

    matrice = [[0] * len(aretes) for _ in range(len(sommets))]

    for j, (s1, s2, orientee) in enumerate(aretes):
        if orientee:
            matrice[s1][j] = -1
            matrice[s2][j] = 1
        else:
            matrice[s1][j] = 1
            matrice[s2][j] = 1

    for widget in data['matrice_inc_frame'].winfo_children():
        widget.destroy()

    titre = tk.Label(data['matrice_inc_frame'], text="Matrice d'Incidence", font=('Helvetica', 14, 'bold'))
    titre.grid(row=0, column=0, columnspan=len(aretes) + 1, pady=10)

    for j in range(len(aretes)):
        tk.Label(data['matrice_inc_frame'], text=f"A{j+1}", width=10, relief="solid").grid(row=1, column=j+1)

    for i in range(len(sommets)):
        tk.Label(data['matrice_inc_frame'], text=f"{i+1}", width=10, relief="solid").grid(row=i+2, column=0)

    for i, row in enumerate(matrice):
        for j, val in enumerate(row):
            tk.Label(data['matrice_inc_frame'], text=str(val), width=10, relief="solid").grid(row=i+2, column=j+1)

#Matrice adjacence
def generer_matrice_adjacente():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    matrice = [[0] * n for _ in range(n)]  # Crée une matrice n x n remplie de 0

    # Remplir la matrice avec les arêtes
    for s1, s2, orientee in aretes:
        if orientee:
            matrice[s1][s2] = 1  # Arête orientée de s1 à s2
        else:
            matrice[s1][s2] = 1  # Arête non orientée de s1 à s2
            matrice[s2][s1] = 1  # Symétrie pour l'arête non orientée

    # Effacer le contenu précédent du cadre de matrice
    for widget in data['matrice_adj_frame'].winfo_children():
        widget.destroy()

    # Ajouter un titre à la matrice
    titre = tk.Label(data['matrice_adj_frame'], text="Matrice d'Adjacence", font=('Helvetica', 14, 'bold'))
    titre.grid(row=0, column=0, columnspan=n+1, pady=10)

    # Afficher les étiquettes pour les colonnes en haut
    for j in range(n):
        label = tk.Label(data['matrice_adj_frame'], text=f"{j+1}", width=10, relief="solid", anchor="center")
        label.grid(row=1, column=j+1)  # Notez column=j+1 pour éviter la colonne 0

    # Afficher les étiquettes pour les lignes sur le côté gauche
    for i in range(n):
        label = tk.Label(data['matrice_adj_frame'], text=f"{i+1}", width=10, relief="solid", anchor="center")
        label.grid(row=i+2, column=0)  # Notez row=i+2 pour tenir compte du titre

    # Afficher la matrice
    for i in range(n):
        for j in range(n):
            label = tk.Label(data['matrice_adj_frame'], text=str(matrice[i][j]), width=10, relief="solid", anchor="center")
            label.grid(row=i+2, column=j+1)
      
def est_valide(sommet, chaine, visites, matrice_adj):
    # Vérifie si le sommet peut être ajouté à la chaîne
    dernier_sommet = chaine[-1]
    if visites[sommet] == 1:  # Si le sommet a déjà été visité
        return False
    if matrice_adj[dernier_sommet][sommet] == 0:  # Si il n'y a pas d'arête entre le dernier sommet et celui-ci
        return False
    return True

def trouver_chaine_hamiltonienne(matrice_adj, n):
    chaine = []
    visites = [0] * n  # 0 pour non-visité, 1 pour visité
    
    # Commence avec le premier sommet
    chaine.append(0)
    visites[0] = 1
    
    # Tente de construire la chaîne en utilisant le backtracking
    if backtrack(matrice_adj, n, chaine, visites):
        return chaine
    else:
        return None

def backtrack(matrice_adj, n, chaine, visites):
    if len(chaine) == n:  # Si la chaîne contient tous les sommets
        return True
    
    for sommet in range(n):
        if est_valide(sommet, chaine, visites, matrice_adj):
            chaine.append(sommet)
            visites[sommet] = 1
            if backtrack(matrice_adj, n, chaine, visites):  # Appel récursif
                return True
            # Retour en arrière
            chaine.pop()
            visites[sommet] = 0
    
    return False

def afficher_chaine_hamiltonienne():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]
    
    # Remplir la matrice d'adjacence
    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:  # Pour les arêtes non orientées
            matrice_adj[s2][s1] = 1
    
    # Trouver la chaîne hamiltonienne
    chaine = trouver_chaine_hamiltonienne(matrice_adj, n)
    
    if chaine:
        chaine_window = tk.Toplevel(fenetre)
        chaine_window.title("Chaîne Hamiltonienne")
        chaine_label = tk.Label(chaine_window, 
                                text=" -> ".join([f"{i+1}" for i in chaine]), 
                                font=("Helvetica", 12))
        chaine_label.pack(padx=10, pady=10)
    else:
        tk.messagebox.showinfo("Résultat", "Aucune chaîne hamiltonienne trouvée.")
        
def supprimer_arete(matrice_adj, u, v):
    matrice_adj[u][v] = 0
    matrice_adj[v][u] = 0

def dfs(matrice_adj, n, sommet, visites, parcours, arbre):
    visites[sommet] = True
    parcours.append(sommet)
    for voisin in range(n):
        if matrice_adj[sommet][voisin] == 1 and not visites[voisin]:
            arbre.append((sommet, voisin))
            dfs(matrice_adj, n, voisin, visites, parcours, arbre)

# Fonction pour supprimer une arête dans la matrice d'adjacence
def est_connexe(matrice_adj, n):
    visit = [False] * n

    def dfs(v):
        visit[v] = True
        for i in range(n):
            if matrice_adj[v][i] == 1 and not visit[i]:
                dfs(i)

    # Trouver un sommet de départ
    for i in range(n):
        if sum(matrice_adj[i]) > 0:
            start_vertex = i
            break
    else:
        return True  # Pas d'arêtes

    # Effectuer un DFS depuis le sommet de départ
    dfs(start_vertex)

    # Vérifier si tous les sommets connectés ont été visités
    for i in range(n):
        if sum(matrice_adj[i]) > 0 and not visit[i]:
            return False
    return True

def trouver_chaine_eulerienne(matrice_adj, n):
    impairs = [i for i in range(n) if sum(matrice_adj[i]) % 2 != 0]
    if len(impairs) not in [0, 2]:
        return None  # Pas de chaîne eulérienne possible
    
    if not est_connexe(matrice_adj, n):
        return None
    
    sommet_de_depart = impairs[0] if len(impairs) == 2 else 0

    chaine = []
    def fleury(matrice_adj, sommet):
        for voisin in range(n):
            if matrice_adj[sommet][voisin] == 1:
                supprimer_arete(matrice_adj, sommet, voisin)
                chaine.append((sommet, voisin))
                fleury(matrice_adj, voisin)

    fleury(matrice_adj, sommet_de_depart)
    
    return chaine
# Fonction pour afficher la chaîne eulérienne

def afficher_chaine_eulerienne():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']

    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]

    # Remplir la matrice d'adjacence
    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:  # Pour les arêtes non orientées
            matrice_adj[s2][s1] = 1

    chaine = trouver_chaine_eulerienne(matrice_adj, n)
    
    if chaine:
        chaine_window = tk.Toplevel(fenetre)
        chaine_window.title("Chaîne Eulérienne")
        chaine_label = tk.Label(chaine_window, 
                                text=" -> ".join([f"{u+1}-{v+1}" for u, v in chaine]), 
                                font=("Helvetica", 12))
        chaine_label.pack(padx=10, pady=10)
    else:
        tk.messagebox.showinfo("Résultat", "Aucune chaîne eulérienne trouvée.")

# Fonction pour dessiner l'arbre couvrant sur un canvas
def dessiner_arbre_couvrant(canvas, arbre, sommets):
    canvas.delete("all")
    rayon = 20
    positions = {}
    
    # Disposition des niveaux pour chaque sommet
    niveau = {}
    enfants = {s: [] for s in range(len(sommets))}  # Initialiser pour tous les sommets
    
    # Construction de l'arbre des enfants
    for parent, enfant in arbre:
        enfants[parent].append(enfant)
    
    # Trouver les composantes connexes
    composantes = []
    visites = set()
    
    def trouver_composante(depart):
        comp = []
        queue = [depart]
        while queue:
            sommet = queue.pop(0)
            if sommet not in visites:
                visites.add(sommet)
                comp.append(sommet)
                for enfant in enfants[sommet]:
                    if enfant not in visites:
                        queue.append(enfant)
        return comp
    
    # Identifier toutes les composantes
    for sommet in range(len(sommets)):
        if sommet not in visites:
            comp = trouver_composante(sommet)
            composantes.append(comp)
    
    # Calculer les niveaux pour chaque composante
    niveau_global = 0
    for composante in composantes:
        if not composante:
            continue
            
        # BFS pour déterminer les niveaux dans cette composante
        racine = composante[0]
        queue = [(racine, 0)]
        niveau[racine] = 0
        
        while queue:
            sommet, niv = queue.pop(0)
            for enfant in enfants[sommet]:
                if enfant not in niveau:
                    niveau[enfant] = niv + 1
                    queue.append((enfant, niv + 1))
        
        # Calculer la largeur maximale de chaque niveau dans la composante
        largeur_niveaux = {}
        for s in composante:
            niv = niveau.get(s, 0)
            largeur_niveaux[niv] = largeur_niveaux.get(niv, 0) + 1
        
        # Positionner les sommets de la composante
        positions_niveau = {niv: 0 for niv in largeur_niveaux}
        max_largeur = max(largeur_niveaux.values())
        
        for s in composante:
            niv = niveau.get(s, 0)
            pos_x = positions_niveau[niv]
            espacement_h = 800 / (max_largeur + 1)
            espacement_v = 100
            
            x = 100 + espacement_h * pos_x
            y = 100 + espacement_v * (niv + niveau_global)
            
            positions[s] = (x, y)
            positions_niveau[niv] += 1
        
        # Mettre à jour le niveau global pour la prochaine composante
        max_niveau = max(niveau[s] for s in composante) if composante else 0
        niveau_global += max_niveau + 2
    
    # Dessiner les sommets
    for s in positions:
        x, y = positions[s]
        canvas.create_oval(x-rayon, y-rayon, x+rayon, y+rayon, fill='orange')
        canvas.create_text(x, y, text=f"{s+1}")
    
    # Dessiner les arêtes
    for u, v in arbre:
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        
        angle1 = math.atan2(y2 - y1, x2 - x1)
        angle2 = math.atan2(y1 - y2, x1 - x2)
        
        start_x = x1 + rayon * math.cos(angle1)
        start_y = y1 + rayon * math.sin(angle1)
        end_x = x2 + rayon * math.cos(angle2)
        end_y = y2 + rayon * math.sin(angle2)
        
        canvas.create_line(start_x, start_y, end_x, end_y, fill='black',width=4)

def parcours_largeur():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]
    
    # Remplir la matrice d'adjacence
    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:
            matrice_adj[s2][s1] = 1
    
    # Début du parcours
    visite = [False] * n
    parcours = []
    arbre = []
    
    def bfs_composante(depart):
        queue = [depart]
        visite[depart] = True
        parcours.append(depart)  # Ajouter le sommet de départ au parcours
        while queue:
            sommet = queue.pop(0)
            for voisin in range(n):
                if matrice_adj[sommet][voisin] == 1 and not visite[voisin]:
                    visite[voisin] = True
                    queue.append(voisin)
                    arbre.append((sommet, voisin))
                    parcours.append(voisin)  # Ajouter le voisin au parcours

    # Parcourir toutes les composantes connexes
    for sommet in range(n):
        if not visite[sommet]:
            bfs_composante(sommet)
    
    # Affichage
    parcours_window = tk.Toplevel(fenetre)
    parcours_window.title("Parcours en Largeur")
    
    frame = tk.Frame(parcours_window)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Ajouter une scrollbar verticale
    v_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    canvas = tk.Canvas(frame, width=400, height=400, bg='white', yscrollcommand=v_scroll.set)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    v_scroll.config(command=canvas.yview)
    
    # Dessiner l'arbre couvrant
    dessiner_arbre_couvrant(canvas, arbre, sommets)
    
    # Affichage de la liste du parcours
    label = tk.Label(parcours_window, text=" -> ".join([f"{i+1}" for i in parcours]), font=("Helvetica", 12))
    label.pack(padx=10, pady=10)

    # Définir la région de défilement
    canvas.config(scrollregion=canvas.bbox("all"))

    # Debug
    print("Parcours (Largeur) :", parcours)  # Pour vérifier le contenu

def parcours_profondeur():
    current_tab = notebook.nametowidget(notebook.select())
    data = tab_data[str(current_tab)]
    sommets = data['sommets']
    aretes = data['aretes']

    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]

    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:
            matrice_adj[s2][s1] = 1

    visite = [False] * n
    parcours = []
    arbre = []

    for sommet in range(n):
        if not visite[sommet]:
            dfs(matrice_adj, n, sommet, visite, parcours, arbre)

    # Affichage dans une nouvelle fenêtre
    profondeur_window = tk.Toplevel(fenetre)
    profondeur_window.title("Parcours en Profondeur")

    frame = tk.Frame(profondeur_window)
    frame.pack(fill=tk.BOTH, expand=True)

    v_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(frame, width=400, height=400, bg='white', yscrollcommand=v_scroll.set)
    canvas.pack(fill=tk.BOTH, expand=True)

    v_scroll.config(command=canvas.yview)

    dessiner_arbre_couvrant(canvas, arbre, sommets)

    label = tk.Label(profondeur_window, text=" -> ".join([f"{i+1}" for i in parcours]), font=("Helvetica", 12))
    label.pack(padx=10, pady=10)

    canvas.config(scrollregion=canvas.bbox("all"))

    print("Parcours (Profondeur) :", parcours)

# Créer la barre de menu
mon_menu = Menu(fenetre)

# Menu Fichier
file_menu = Menu(mon_menu, tearoff=0)
file_menu.add_command(label="Nouveau", command=nouveau)
file_menu.add_command(label="Ouvrir", command=ouvrir_fichier)
file_menu.add_command(label="Enregistrer", command=enregistrer_fichier)
file_menu.add_command(label="Enregistrer sous", command=enregistrer_sous)


file_menu.add_separator()
file_menu.add_command(label="Fermer", command=fermer_fichier)
file_menu.add_command(label="Quitter", command=quitter_application)
mon_menu.add_cascade(label="Fichier", menu=file_menu)

# Menu Création
creation_menu = tk.Menu(mon_menu, tearoff=0)
graphe_menu = tk.Menu(creation_menu, tearoff=0)
graphe_menu.add_command(label="Sommet", command=creer_sommet)
arete_menu = tk.Menu(graphe_menu, tearoff=0)
arete_menu.add_command(label="Orientée", command=creer_arete_oriente)
arete_menu.add_command(label="Non-orientée", command=creer_arete_non_oriente)
graphe_menu.add_cascade(label="Arête", menu=arete_menu)
creation_menu.add_cascade(label="Graphe", menu=graphe_menu)
mon_menu.add_cascade(label="Création", menu=creation_menu)

# Menu Affichage
affichage_menu = tk.Menu(mon_menu, tearoff=0)
chaine_menu = tk.Menu(affichage_menu, tearoff=0)
affichage_menu.add_command(label="Graphe", command=afficher_graphe_networkx)
chaine_menu.add_command(label='Hamiltonienne',command=afficher_chaine_hamiltonienne)
chaine_menu.add_command(label='Eulerienne',command=afficher_chaine_eulerienne)
affichage_menu.add_cascade(label='Chaînes', menu=chaine_menu)

# Matrices Menu
matrice_menu = tk.Menu(affichage_menu, tearoff=0)
matrice_menu.add_command(label='Incidente', command=generer_matrice_incidence)
matrice_menu.add_command(label='Adjacente',command=generer_matrice_adjacente)
affichage_menu.add_cascade(label='Matrices', menu=matrice_menu)
mon_menu.add_cascade(label="Affichage", menu=affichage_menu)
chemin_menu = tk.Menu(affichage_menu, tearoff=0)

# Exécution
execution_menu = tk.Menu(mon_menu, tearoff=0)
execution_menu.add_command(label="Parcours en largeur", command=parcours_largeur)
execution_menu.add_command(label="Parcours en profondeur", command=parcours_profondeur)
mon_menu.add_cascade(label="Exécution", menu=execution_menu)

# Edition
edition_menu = tk.Menu(mon_menu, tearoff=0)
edition_menu.add_command(label="Graphe")  # Sous-menu "Graphe"
mon_menu.add_cascade(label="Edition", menu=edition_menu)  # Ajout du menu "Edition" au menu principal



# Afficher la barre de menu
fenetre.config(menu=mon_menu)

# Lancer la boucle principale de l'interface
fenetre.mainloop()
import tkinter as tk
from tkinter import Canvas, Menu, filedialog, messagebox
from tkinter import ttk
import math
from tkinter import simpledialog

afficher_etiquettes_aretes = False  # Variable d'état pour afficher les étiquettes des arêtes

# Dictionnaire pour stocker les sommets et arêtes de chaque onglet
tab_data = {}

# Variables globales pour la création
creation_sommet = False
creation_arete = False
arete_orientee = False
sommet_selectionne = None  # Sommet sélectionné pour ajouter une arête
current_file = None  # Fichier en cours

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
    matrice_frame_tab = tk.Frame(new_tab)
    matrice_frame_tab.pack(pady=10)
    
    matrice_adj_frame_tab = tk.Frame(matrice_frame_tab)
    matrice_adj_frame_tab.pack(side=tk.LEFT, padx=10)
    
    matrice_inc_frame_tab = tk.Frame(matrice_frame_tab)
    matrice_inc_frame_tab.pack(side=tk.LEFT, padx=10)
    
    notebook.add(new_tab, text="Nouveau Graphe")
    notebook.select(new_tab)
    
    # Initialiser les données pour le nouvel onglet
    tab_data[str(new_tab)] = {
        'sommets': [],
        'aretes': set(),  # Utiliser un ensemble pour éviter les doublons
        'arete_orientee': False,
        'matrice_adj_frame': matrice_adj_frame_tab,
        'matrice_inc_frame': matrice_inc_frame_tab,
        'type_arete': None
    }

def ouvrir_fichier():
    global current_file
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers Python", "*.py")])
    if file_path:
        current_file = file_path
        new_tab = tk.Frame(notebook)
        
        # Créer le canvas avec scrollbars
        canvas_frame = tk.Frame(new_tab)
        canvas_frame.pack(expand=1, fill='both')
        
        canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar_y = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient='horizontal', command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Cadre pour les matrices
        matrice_frame_tab = tk.Frame(new_tab)
        matrice_frame_tab.pack(pady=10)
        
        matrice_adj_frame_tab = tk.Frame(matrice_frame_tab)
        matrice_adj_frame_tab.pack(side=tk.LEFT, padx=10)
        
        matrice_inc_frame_tab = tk.Frame(matrice_frame_tab)
        matrice_inc_frame_tab.pack(side=tk.LEFT, padx=10)
        
        notebook.add(new_tab, text=file_path.split('/')[-1])
        notebook.select(new_tab)

        try:
            with open(file_path, 'r') as file:
                contenu = file.read()

            namespace = {}
            exec(contenu, namespace)

            # Initialiser les données pour le nouvel onglet
            aretes_chargees = set(namespace.get('aretes', []))
            
            tab_data[str(new_tab)] = {
                'sommets': namespace.get('sommets', []),
                'aretes': aretes_chargees,
                'arete_orientee': namespace.get('arete_orientee', False),
                'matrice_adj_frame': matrice_adj_frame_tab,
                'matrice_inc_frame': matrice_inc_frame_tab,
                'type_arete': 'orientée' if namespace.get('arete_orientee', False) else 'non orientée'
            }

            # Dessiner le graphe avec les données chargées
            dessiner_graphe(canvas, str(new_tab))

            # Demander à l'utilisateur s'il veut modifier le graphe
            reponse = messagebox.askyesno("Modifier le Graphe", "Voulez-vous modifier votre graphe ?")

            if reponse:
                global creation_sommet, creation_arete, sommet_selectionne
                creation_sommet = True
                creation_arete = False
                sommet_selectionne = None
                canvas.bind("<Button-1>", lambda event: canvas_click(event, canvas))

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier : {e}")

# Fonction pour enregistrer le fichier actuel
def enregistrer_fichier():
    global current_file
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)
    if current_file:
        with open(current_file, 'w') as file:
            file.write(sauvegarder_graphe(tab_key))
    else:
        enregistrer_sous()

# Fonction pour enregistrer sous le fichier actuel
def enregistrer_sous():
    global current_file
    fichier = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Fichiers Python", "*.py")])
    if fichier:
        current_tab = notebook.nametowidget(notebook.select())
        tab_key = str(current_tab)
        with open(fichier, 'w') as file:
            file.write(sauvegarder_graphe(tab_key))
            current_file = fichier
            notebook.tab(notebook.select(), text=fichier.split('/')[-1])

# Fonction pour fermer l'onglet actuel
def fermer_fichier():
    global current_file
    current_tab = notebook.select()
    if current_tab:
        tab_key = str(current_tab)
        if tab_key in tab_data:
            del tab_data[tab_key]
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
    tab_data[tab_key]['arete_orientee'] = True
    tab_data[tab_key]['type_arete'] = 'orientée'

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
    tab_data[tab_key]['arete_orientee'] = False
    tab_data[tab_key]['type_arete'] = 'non orientée'

# Fonction pour dessiner une arête orientée (flèche)
def draw_arrow(canvas, x1, y1, x2, y2):
    # Calculer l'angle de la ligne
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Longueur et largeur de la flèche
    arrow_length = 15
    arrow_width = 5
    
    # Trouver le rayon du sommet
    rayon = 10
    
    # Calculer les positions des points de départ et d'arrivée
    start_x = x1 + (rayon * math.cos(angle))
    start_y = y1 + (rayon * math.sin(angle))
    end_x = x2 - (rayon * math.cos(angle))
    end_y = y2 - (rayon * math.sin(angle))
    
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
        if math.sqrt((sx - nouveau_sommet[0]) ** 2 + (sy - nouveau_sommet[1]) ** 2) < seuil:
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
            dessiner_graphe(canvas, str(current_tab))
        else:
            messagebox.showerror("Erreur", "Le sommet est trop proche d'un sommet existant.")
    
    elif creation_arete:
        for i, (sx, sy) in enumerate(sommets):
            if math.sqrt((sx - x) ** 2 + (sy - y) ** 2) <= 10:
                if sommet_selectionne is None:
                    sommet_selectionne = i
                else:
                    orientee = data['arete_orientee']
                    if orientee:
                        aretes.add((sommet_selectionne, i, True))
                    else:
                        aretes.add((sommet_selectionne, i, False))
                    
                    dessiner_etiquette_arete(canvas, sommets, sommet_selectionne, i, len(aretes) - 1)
                    sommet_selectionne = None
                break
    
    dessiner_graphe(canvas, str(current_tab))
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

# Sauvegarder le graphe dans un format lisible
def sauvegarder_graphe(current_tab):
    tab_key = str(current_tab)
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    arete_orientee = data['arete_orientee']
    
    graphe_data = f"sommets = {sommets}\naretes = {list(aretes)}\narete_orientee = {arete_orientee}\n"
    return graphe_data

# Fonction pour afficher le graphe
def afficher_graphe():
    if not notebook.tabs():
        messagebox.showerror("Erreur", "Aucun onglet n'existe. Veuillez en créer un d'abord.")
        return

    selected_tab_id = notebook.select()
    if not selected_tab_id:
        notebook.select(notebook.tabs()[0])
        selected_tab_id = notebook.select()

    current_tab = notebook.nametowidget(selected_tab_id)
    
    # Trouver le canvas dans l'onglet
    for widget in current_tab.winfo_children():
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, tk.Canvas):
                    dessiner_graphe(child, str(current_tab))
                    return
    
    messagebox.showerror("Erreur", "Aucun canvas trouvé dans l'onglet.")

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
affichage_menu.add_command(label="Graphe", command=afficher_graphe)
mon_menu.add_cascade(label="Affichage", menu=affichage_menu)

# Afficher la barre de menu
fenetre.config(menu=mon_menu)

# Lancer la boucle principale de l'interface
fenetre.mainloop()
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

# Variable globale pour garder la trace du nombre de sommets
sommets_count = 0

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
        'type_arete': None,
        'matrice_adj_frame': matrice_adj_frame_tab,
        'matrice_inc_frame': matrice_inc_frame_tab,
        'canvas': canvas
    }

def ouvrir_fichier():
    global current_file, sommets_count
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers Python", "*.py"), ("Tous les fichiers", "*.*")])
    if file_path:
        current_file = file_path
        new_tab = tk.Frame(notebook)
        
        # Créer un canvas pour le nouvel onglet
        canvas_frame = tk.Frame(new_tab)
        canvas_frame.pack(expand=1, fill='both')
        
        canvas = tk.Canvas(canvas_frame, bg='white')
        canvas.pack(expand=1, fill='both')
        
        notebook.add(new_tab, text=file_path.split('/')[-1])
        notebook.select(new_tab)

        try:
            with open(file_path, 'r') as file:
                contenu = file.read()

            namespace = {}
            exec(contenu, namespace)

            # Initialiser les données pour le nouvel onglet
            aretes_chargees = namespace.get('aretes', [])
            aretes_orientees_chargees = namespace.get('aretes_orientees', [])
            
            # Convertir les arêtes en format interne (s1, s2, orientee)
            aretes_internes = set()
            for arete in aretes_chargees:
                if len(arete) == 2:
                    aretes_internes.add((arete[0], arete[1], False))
            
            for arete in aretes_orientees_chargees:
                if len(arete) == 2:
                    aretes_internes.add((arete[0], arete[1], True))

            # Déterminer le type d'arête
            type_arete = None
            if aretes_orientees_chargees:
                type_arete = 'orientée'
            elif aretes_chargees:
                type_arete = 'non orientée'

            tab_data[str(new_tab)] = {
                'sommets': namespace.get('sommets', []),
                'aretes': aretes_internes,
                'arete_orientee': type_arete == 'orientée',
                'type_arete': type_arete,
                'matrice_adj_frame': None,
                'matrice_inc_frame': None,
                'canvas': canvas
            }

            # Mettre à jour le compteur de sommets
            sommets_count = len(tab_data[str(new_tab)]['sommets'])

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

def enregistrer_fichier():
    global current_file
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab:
        tab_key = str(current_tab)
        if current_file:
            with open(current_file, 'w') as file:
                file.write(sauvegarder_graphe(tab_key))
        else:
            enregistrer_sous()

def enregistrer_sous():
    global current_file
    fichier = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Fichiers Python", "*.py")])
    if fichier:
        current_tab = notebook.nametowidget(notebook.select())
        if current_tab:
            tab_key = str(current_tab)
            with open(fichier, 'w') as file:
                file.write(sauvegarder_graphe(tab_key))
            current_file = fichier
            notebook.tab(notebook.select(), text=fichier.split('/')[-1])

def fermer_fichier():
    global current_file
    current_tab = notebook.select()
    if current_tab:
        tab_key = str(current_tab)
        if tab_key in tab_data:
            del tab_data[tab_key]
        notebook.forget(current_tab)
        current_file = None

def quitter_application():
    confirmation = messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?")
    if confirmation:
        fenetre.quit()

def creer_sommet():
    global creation_sommet, creation_arete
    creation_sommet = True
    creation_arete = False

def creer_arete_oriente():
    global creation_sommet, creation_arete
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab:
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
    if current_tab:
        tab_key = str(current_tab)

        # Vérifier si un type d'arête a déjà été créé
        if 'type_arete' in tab_data[tab_key] and tab_data[tab_key]['type_arete'] is not None and tab_data[tab_key]['type_arete'] != 'non orientée':
            messagebox.showerror("Erreur", "Vous ne pouvez pas créer des arêtes orientées et non orientées dans le même onglet.")
            return

        creation_sommet = False
        creation_arete = True
        tab_data[tab_key]['arete_orientee'] = False
        tab_data[tab_key]['type_arete'] = 'non orientée'

def dessiner_graphe(canvas, current_tab):
    canvas.delete("all")
    if current_tab not in tab_data:
        return
        
    data = tab_data[current_tab]
    sommets = data['sommets']
    aretes = data['aretes']
    
    # Dessiner les arêtes
    for s1, s2, orientee in aretes:
        if s1 < len(sommets) and s2 < len(sommets):
            x1, y1 = sommets[s1]
            x2, y2 = sommets[s2]
            
            if orientee:
                draw_arrow(canvas, x1, y1, x2, y2)
            else:
                canvas.create_line(x1, y1, x2, y2, width=2, tags="arete")
    
    # Dessiner les sommets
    for i, (x, y) in enumerate(sommets):
        canvas.create_oval(x-10, y-10, x+10, y+10, fill="blue", tags="sommet")
        canvas.create_text(x, y, text=str(i+1), fill="white", tags="sommet_text")

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

def sommet_trop_proche(nouveau_sommet, sommets_existants, seuil=20):
    for sx, sy in sommets_existants:
        if math.sqrt((sx - nouveau_sommet[0]) ** 2 + (sy - nouveau_sommet[1]) ** 2) < seuil:
            return True
    return False

def canvas_click(event, canvas):
    global sommet_selectionne
    current_tab = notebook.nametowidget(notebook.select())
    if not current_tab:
        return
        
    tab_key = str(current_tab)
    if tab_key not in tab_data:
        return
        
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    
    if creation_sommet:
        nouveau_sommet = (x, y)
        if not sommet_trop_proche(nouveau_sommet, sommets):
            sommets.append(nouveau_sommet)
            dessiner_graphe(canvas, tab_key)
        else:
            messagebox.showerror("Erreur", "Le sommet est trop proche d'un sommet existant.")
    
    elif creation_arete:
        for i, (sx, sy) in enumerate(sommets):
            if math.sqrt((sx - x) ** 2 + (sy - y) ** 2) <= 10:
                if sommet_selectionne is None:
                    sommet_selectionne = i
                else:
                    if sommet_selectionne != i:  # Éviter les boucles sur le même sommet
                        orientee = data['arete_orientee']
                        nouvelle_arete = (sommet_selectionne, i, orientee)
                        if nouvelle_arete not in aretes:
                            aretes.add(nouvelle_arete)
                        sommet_selectionne = None
                    else:
                        messagebox.showerror("Erreur", "Impossible de créer une arête sur le même sommet.")
                        sommet_selectionne = None
                break
        dessiner_graphe(canvas, tab_key)

def sauvegarder_graphe(current_tab):
    if current_tab not in tab_data:
        return ""
        
    data = tab_data[current_tab]
    sommets = data['sommets']
    aretes = data['aretes']
    
    # Séparer les arêtes orientées et non orientées
    aretes_non_orientees = []
    aretes_orientees = []
    
    for s1, s2, orientee in aretes:
        if orientee:
            aretes_orientees.append([s1, s2])
        else:
            aretes_non_orientees.append([s1, s2])
    
    graphe_data = f"sommets = {sommets}\n"
    if aretes_non_orientees:
        graphe_data += f"aretes = {aretes_non_orientees}\n"
    if aretes_orientees:
        graphe_data += f"aretes_orientees = {aretes_orientees}\n"
    
    return graphe_data

def afficher_graphe():
    if not notebook.tabs():
        messagebox.showerror("Erreur", "Aucun onglet n'existe. Veuillez en créer un d'abord.")
        return

    selected_tab_id = notebook.select()
    if not selected_tab_id:
        notebook.select(notebook.tabs()[0])
        selected_tab_id = notebook.select()

    current_tab = notebook.nametowidget(selected_tab_id)
    tab_key = str(current_tab)
    
    if tab_key in tab_data and 'canvas' in tab_data[tab_key]:
        canvas = tab_data[tab_key]['canvas']
        dessiner_graphe(canvas, tab_key)
    else:
        messagebox.showerror("Erreur", "Aucun canvas associé à cet onglet.")

# Fonction pour générer la matrice d'incidence
def generer_matrice_incidence():
    current_tab = notebook.nametowidget(notebook.select())
    if not current_tab:
        messagebox.showerror("Erreur", "Aucun onglet sélectionné")
        return
        
    tab_key = str(current_tab)
    if tab_key not in tab_data:
        messagebox.showerror("Erreur", "Aucune donnée pour cet onglet")
        return
        
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = list(data['aretes'])

    if not aretes:
        messagebox.showinfo("Info", "Aucune arête à afficher")
        return

    matrice = [[0] * len(aretes) for _ in range(len(sommets))]

    for j, (s1, s2, orientee) in enumerate(aretes):
        if s1 < len(sommets) and s2 < len(sommets):
            if orientee:
                matrice[s1][j] = -1
                matrice[s2][j] = 1
            else:
                matrice[s1][j] = 1
                matrice[s2][j] = 1

    # Utiliser le frame principal si aucun frame spécifique n'est défini
    frame_cible = data.get('matrice_inc_frame', matrice_inc_frame)
    
    for widget in frame_cible.winfo_children():
        widget.destroy()

    titre = tk.Label(frame_cible, text="Matrice d'Incidence", font=('Helvetica', 14, 'bold'))
    titre.grid(row=0, column=0, columnspan=len(aretes) + 1, pady=10)

    for j in range(len(aretes)):
        tk.Label(frame_cible, text=f"A{j+1}", width=10, relief="solid").grid(row=1, column=j+1)

    for i in range(len(sommets)):
        tk.Label(frame_cible, text=f"{i+1}", width=10, relief="solid").grid(row=i+2, column=0)

    for i, row in enumerate(matrice):
        for j, val in enumerate(row):
            tk.Label(frame_cible, text=str(val), width=10, relief="solid").grid(row=i+2, column=j+1)

# Matrice adjacence
def generer_matrice_adjacente():
    current_tab = notebook.nametowidget(notebook.select())
    if not current_tab:
        messagebox.showerror("Erreur", "Aucun onglet sélectionné")
        return
        
    tab_key = str(current_tab)
    if tab_key not in tab_data:
        messagebox.showerror("Erreur", "Aucune donnée pour cet onglet")
        return
        
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    if n == 0:
        messagebox.showinfo("Info", "Aucun sommet à afficher")
        return
        
    matrice = [[0] * n for _ in range(n)]

    # Remplir la matrice avec les arêtes
    for s1, s2, orientee in aretes:
        if s1 < n and s2 < n:
            if orientee:
                matrice[s1][s2] = 1
            else:
                matrice[s1][s2] = 1
                matrice[s2][s1] = 1

    # Utiliser le frame principal si aucun frame spécifique n'est défini
    frame_cible = data.get('matrice_adj_frame', matrice_adj_frame)
    
    # Effacer le contenu précédent du cadre de matrice
    for widget in frame_cible.winfo_children():
        widget.destroy()

    # Ajouter un titre à la matrice
    titre = tk.Label(frame_cible, text="Matrice d'Adjacence", font=('Helvetica', 14, 'bold'))
    titre.grid(row=0, column=0, columnspan=n+1, pady=10)

    # Afficher les étiquettes pour les colonnes en haut
    for j in range(n):
        label = tk.Label(frame_cible, text=f"{j+1}", width=10, relief="solid", anchor="center")
        label.grid(row=1, column=j+1)

    # Afficher les étiquettes pour les lignes sur le côté gauche
    for i in range(n):
        label = tk.Label(frame_cible, text=f"{i+1}", width=10, relief="solid", anchor="center")
        label.grid(row=i+2, column=0)

    # Afficher la matrice
    for i in range(n):
        for j in range(n):
            label = tk.Label(frame_cible, text=str(matrice[i][j]), width=10, relief="solid", anchor="center")
            label.grid(row=i+2, column=j+1)

def est_valide(sommet, chaine, visites, matrice_adj):
    if not chaine:
        return True
        
    dernier_sommet = chaine[-1]
    if visites[sommet] == 1:
        return False
    if matrice_adj[dernier_sommet][sommet] == 0:
        return False
    return True

def trouver_chaine_hamiltonienne(matrice_adj, n):
    if n == 0:
        return None
        
    # Essayer chaque sommet comme point de départ
    for start in range(n):
        chaine = [start]
        visites = [0] * n
        visites[start] = 1
        
        if backtrack_hamiltonien(matrice_adj, n, chaine, visites):
            return chaine
            
    return None

def backtrack_hamiltonien(matrice_adj, n, chaine, visites):
    if len(chaine) == n:
        return True
        
    for sommet in range(n):
        if est_valide(sommet, chaine, visites, matrice_adj):
            chaine.append(sommet)
            visites[sommet] = 1
            if backtrack_hamiltonien(matrice_adj, n, chaine, visites):
                return True
            chaine.pop()
            visites[sommet] = 0
            
    return False

def afficher_chaine_hamiltonienne():
    current_tab = notebook.nametowidget(notebook.select())
    if not current_tab:
        messagebox.showerror("Erreur", "Aucun onglet sélectionné")
        return
        
    tab_key = str(current_tab)
    if tab_key not in tab_data:
        messagebox.showerror("Erreur", "Aucune donnée pour cet onglet")
        return
        
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    if n == 0:
        messagebox.showinfo("Info", "Aucun sommet dans le graphe")
        return
        
    matrice_adj = [[0] * n for _ in range(n)]
    
    # Remplir la matrice d'adjacence
    for s1, s2, orientee in aretes:
        if s1 < n and s2 < n:
            matrice_adj[s1][s2] = 1
            if not orientee:
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
        messagebox.showinfo("Résultat", "Aucune chaîne hamiltonienne trouvée.")

def supprimer_arete(matrice_adj, u, v):
    if u < len(matrice_adj) and v < len(matrice_adj):
        matrice_adj[u][v] = 0
        matrice_adj[v][u] = 0

def est_connexe(matrice_adj, n):
    if n == 0:
        return True
        
    visit = [False] * n

    def dfs(v):
        visit[v] = True
        for i in range(n):
            if matrice_adj[v][i] == 1 and not visit[i]:
                dfs(i)

    # Trouver un sommet de départ
    start_vertex = 0
    for i in range(n):
        if sum(matrice_adj[i]) > 0:
            start_vertex = i
            break

    dfs(start_vertex)

    # Vérifier si tous les sommets avec des arêtes ont été visités
    for i in range(n):
        if sum(matrice_adj[i]) > 0 and not visit[i]:
            return False
    return True

def trouver_chaine_eulerienne(matrice_adj, n):
    if n == 0:
        return None
        
    # Compter les degrés impairs
    impairs = [i for i in range(n) if sum(matrice_adj[i]) % 2 != 0]
    
    if len(impairs) not in [0, 2]:
        return None  # Pas de chaîne eulérienne possible
    
    if not est_connexe(matrice_adj, n):
        return None
    
    # Faire une copie de la matrice pour ne pas modifier l'originale
    matrice_temp = [row[:] for row in matrice_adj]
    
    sommet_depart = impairs[0] if len(impairs) == 2 else 0
    chaine = []
    pile = [sommet_depart]
    
    while pile:
        u = pile[-1]
        # Trouver un voisin
        voisin_trouve = -1
        for v in range(n):
            if matrice_temp[u][v] == 1:
                voisin_trouve = v
                break
                
        if voisin_trouve != -1:
            # Supprimer l'arête
            matrice_temp[u][voisin_trouve] = 0
            matrice_temp[voisin_trouve][u] = 0
            pile.append(voisin_trouve)
        else:
            # Aucun voisin trouvé, ajouter au chemin
            if len(pile) > 1:
                chaine.append((pile[-2], pile[-1]))
            pile.pop()
    
    return chaine

def afficher_chaine_eulerienne():
    current_tab = notebook.nametowidget(notebook.select())
    if not current_tab:
        messagebox.showerror("Erreur", "Aucun onglet sélectionné")
        return
        
    tab_key = str(current_tab)
    if tab_key not in tab_data:
        messagebox.showerror("Erreur", "Aucune donnée pour cet onglet")
        return
        
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']

    n = len(sommets)
    if n == 0:
        messagebox.showinfo("Info", "Aucun sommet dans le graphe")
        return

    matrice_adj = [[0] * n for _ in range(n)]

    # Remplir la matrice d'adjacence
    for s1, s2, orientee in aretes:
        if s1 < n and s2 < n:
            matrice_adj[s1][s2] = 1
            if not orientee:
                matrice_adj[s2][s1] = 1

    chaine = trouver_chaine_eulerienne(matrice_adj, n)
    
    if chaine:
        chaine_window = tk.Toplevel(fenetre)
        chaine_window.title("Chaîne Eulérienne")
        chaine_text = " -> ".join([f"{u+1}-{v+1}" for u, v in chaine])
        chaine_label = tk.Label(chaine_window, text=chaine_text, font=("Helvetica", 12))
        chaine_label.pack(padx=10, pady=10)
    else:
        messagebox.showinfo("Résultat", "Aucune chaîne eulérienne trouvée.")

def dessiner_arbre_couvrant(canvas, arbre, sommets):
    canvas.delete("all")
    if not sommets:
        return
        
    rayon = 20
    
    # Calculer les positions en cercle
    n = len(sommets)
    positions = {}
    centre_x, centre_y = 200, 200
    rayon_cercle = min(150, n * 15)
    
    for i in range(n):
        angle = 2 * math.pi * i / n
        x = centre_x + rayon_cercle * math.cos(angle)
        y = centre_y + rayon_cercle * math.sin(angle)
        positions[i] = (x, y)
    
    # Dessiner les arêtes de l'arbre
    for u, v in arbre:
        if u in positions and v in positions:
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            
            # Ajuster les points pour le bord des cercles
            angle = math.atan2(y2 - y1, x2 - x1)
            start_x = x1 + rayon * math.cos(angle)
            start_y = y1 + rayon * math.sin(angle)
            end_x = x2 - rayon * math.cos(angle)
            end_y = y2 - rayon * math.sin(angle)
            
            canvas.create_line(start_x, start_y, end_x, end_y, fill='green', width=3)
    
    # Dessiner les sommets
    for i, (x, y) in positions.items():
        canvas.create_oval(x-rayon, y-rayon, x+rayon, y+rayon, fill='lightblue', outline='black')
        canvas.create_text(x, y, text=str(i+1), font=("Arial", 10, "bold"))

def parcours_largeur():
    current_tab = notebook.nametowidget(notebook.select())
    if not current_tab:
        messagebox.showerror("Erreur", "Aucun onglet sélectionné")
        return
        
    tab_key = str(current_tab)
    if tab_key not in tab_data:
        messagebox.showerror("Erreur", "Aucune donnée pour cet onglet")
        return
        
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    if n == 0:
        messagebox.showinfo("Info", "Aucun sommet dans le graphe")
        return

    matrice_adj = [[0] * n for _ in range(n)]
    
    # Remplir la matrice d'adjacence
    for s1, s2, orientee in aretes:
        if s1 < n and s2 < n:
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
        parcours.append(depart)
        
        while queue:
            sommet = queue.pop(0)
            for voisin in range(n):
                if matrice_adj[sommet][voisin] == 1 and not visite[voisin]:
                    visite[voisin] = True
                    queue.append(voisin)
                    arbre.append((sommet, voisin))
                    parcours.append(voisin)

    # Parcourir toutes les composantes connexes
    for sommet in range(n):
        if not visite[sommet]:
            bfs_composante(sommet)
    
    # Affichage
    parcours_window = tk.Toplevel(fenetre)
    parcours_window.title("Parcours en Largeur")
    parcours_window.geometry("600x500")
    
    # Frame principal
    main_frame = tk.Frame(parcours_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Label du parcours
    parcours_label = tk.Label(main_frame, 
                             text="Parcours: " + " -> ".join([f"{i+1}" for i in parcours]),
                             font=("Helvetica", 12),
                             wraplength=500)
    parcours_label.pack(pady=10)
    
    # Canvas pour l'arbre
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(canvas_frame, width=400, height=300, bg='white')
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Dessiner l'arbre couvrant
    dessiner_arbre_couvrant(canvas, arbre, sommets)
    
    # Ajuster la région de défilement
    canvas.configure(scrollregion=canvas.bbox("all"))

# Mise à jour du menu pour inclure les nouvelles fonctions
# Ajouter ces commandes aux menus existants

# Menu Affichage - Matrices
matrice_menu = tk.Menu(affichage_menu, tearoff=0)
matrice_menu.add_command(label='Incidence', command=generer_matrice_incidence)
matrice_menu.add_command(label='Adjacence', command=generer_matrice_adjacente)
affichage_menu.add_cascade(label='Matrices', menu=matrice_menu)

# Menu Affichage - Chaînes
chaine_menu = tk.Menu(affichage_menu, tearoff=0)
chaine_menu.add_command(label='Hamiltonienne', command=afficher_chaine_hamiltonienne)
chaine_menu.add_command(label='Eulerienne', command=afficher_chaine_eulerienne)
affichage_menu.add_cascade(label='Chaînes', menu=chaine_menu)

# Menu Exécution
execution_menu = tk.Menu(mon_menu, tearoff=0)
execution_menu.add_command(label="Parcours en largeur", command=parcours_largeur)
mon_menu.add_cascade(label="Exécution", menu=execution_menu)

# Lancer la boucle principale
fenetre.mainloop()

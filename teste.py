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

    # Canvas pour le graphe
    canvas_frame = tk.Frame(new_tab)
    canvas_frame.pack(expand=1, fill='both')

    canvas = tk.Canvas(canvas_frame, bg='white')
    new_tab.canvas = canvas

    scrollbar_y = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
    scrollbar_x = tk.Scrollbar(canvas_frame, orient='horizontal', command=canvas.xview)
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    canvas.grid(row=0, column=0, sticky='nsew')
    scrollbar_y.grid(row=0, column=1, sticky='ns')
    scrollbar_x.grid(row=1, column=0, sticky='ew')
    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)

    canvas.bind("<Button-1>", lambda event: canvas_click(event, canvas))

    # Frame parent pour matrices et chaînes
    contenu_frame = tk.Frame(new_tab)
    contenu_frame.pack(pady=10, fill='x')

    # Frame contenant les matrices (au-dessus)
    matrice_frame = tk.Frame(contenu_frame)
    matrice_frame.pack(side=tk.TOP, pady=5, fill='x')

    matrice_adj_frame = tk.Frame(matrice_frame)
    matrice_adj_frame.pack(side=tk.LEFT, padx=10)

    matrice_inc_frame = tk.Frame(matrice_frame)
    matrice_inc_frame.pack(side=tk.LEFT, padx=10)

    # Frame des chaînes (en dessous)
    chaine_frame = tk.Frame(contenu_frame)
    chaine_frame.pack(side=tk.TOP, pady=10, fill='x')

    notebook.add(new_tab, text="Nouveau Graphe")
    notebook.select(new_tab)

    tab_data[str(new_tab)] = {
        'sommets': [],
        'aretes': [],
        'arete_orientee': False,
        'canvas': canvas,
        'matrice_adj_frame': matrice_adj_frame,
        'matrice_inc_frame': matrice_inc_frame,
        'chaine_frame': chaine_frame
    }
    # Also store using the notebook's selected id to make lookups robust
    try:
        tab_data[notebook.select()] = tab_data[str(new_tab)]
    except Exception:
        pass

# Variable globale pour garder la trace du nombre de sommets
sommets_count = 0

# Fonction pour Ouvrir des fichiers de differentes extension
def ouvrir_fichier():
    global current_file, sommets_count, creation_sommet, creation_arete, sommet_selectionne
    creation_sommet = False
    creation_arete = False
    sommet_selectionne = None

    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Tous les fichiers", "*.*"),
            ("Fichiers texte", "*.txt"),
            ("Fichiers Word", "*.docx"),
            ("Fichiers Python", "*.py")
        ]
    )

    if not file_path:
        return

    extension = os.path.splitext(file_path)[1].lower()
    current_file = file_path

    # --- Créer un nouvel onglet ---
    new_tab = tk.Frame(notebook)
    notebook.add(new_tab, text=os.path.basename(file_path))
    notebook.select(new_tab)

    try:
        # =====================
        # CAS 1 : Fichier Python (.py)
        # =====================
        if extension == '.py':
            namespace = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                exec(f.read(), namespace)

            sommets = namespace.get('sommets', [])
            aretes = namespace.get('aretes', [])
            aretes_orientees = namespace.get('aretes_orientees', [])

            # --- Structure principale ---
            contenu_frame = tk.Frame(new_tab)
            contenu_frame.pack(expand=1, fill='both')

            # ==============================
            # 🟩 Partie haute : GRAPHE
            # ==============================
            graphe_frame = tk.Frame(contenu_frame)
            graphe_frame.pack(side=tk.TOP, expand=1, fill='both')

            canvas = tk.Canvas(graphe_frame, bg='white')
            canvas.pack(expand=1, fill='both')

            # Scrollbars
            scrollbar_y = tk.Scrollbar(graphe_frame, orient='vertical', command=canvas.yview)
            scrollbar_y.pack(side='right', fill='y')
            scrollbar_x = tk.Scrollbar(graphe_frame, orient='horizontal', command=canvas.xview)
            scrollbar_x.pack(side='bottom', fill='x')
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

            canvas.bind("<Button-1>", lambda event: canvas_click(event, canvas))

            # ==============================
            # 🟦 Partie basse : Matrices & Chaînes
            # ==============================
            info_frame = tk.Frame(contenu_frame)
            info_frame.pack(pady=10, fill='x')

            # Frame parent pour les matrices (au-dessus)
            matrice_parent = tk.Frame(info_frame)
            matrice_parent.pack(side=tk.TOP, pady=5, fill='x')

            matrice_adj_frame = tk.Frame(matrice_parent)
            matrice_adj_frame.pack(side=tk.LEFT, padx=10)

            matrice_inc_frame = tk.Frame(matrice_parent)
            matrice_inc_frame.pack(side=tk.LEFT, padx=10)

            # Frame des chaînes (en dessous)
            chaine_frame = tk.Frame(info_frame)
            chaine_frame.pack(side=tk.TOP, pady=10, fill='x')

            # --- Enregistrement dans tab_data ---
            # Normaliser les arêtes comme une liste de triplets (s1, s2, orientee)
            normalized_aretes = []
            for edge in aretes:
                try:
                    if len(edge) >= 3:
                        normalized_aretes.append((edge[0], edge[1], bool(edge[2])))
                    elif len(edge) == 2:
                        normalized_aretes.append((edge[0], edge[1], False))
                except Exception:
                    # ignorer les entrées malformées
                    continue

            # si des arêtes orientées séparées ont été fournies
            for edge in aretes_orientees:
                try:
                    if len(edge) >= 2:
                        normalized_aretes.append((edge[0], edge[1], True))
                except Exception:
                    continue

            tab_data[str(new_tab)] = {
                'sommets': sommets,
                'aretes': normalized_aretes,
                'arete_orientee': False,
                'canvas': canvas,
                'matrice_adj_frame': matrice_adj_frame,
                'matrice_inc_frame': matrice_inc_frame,
                'chaine_frame': chaine_frame,
                'info_frame': info_frame,
                'type_arete': None
            }
            # Also store under notebook selected id for consistent lookup
            try:
                tab_data[notebook.select()] = tab_data[str(new_tab)]
            except Exception:
                pass

            sommets_count = len(sommets)

            # --- Dessiner le graphe ---
            dessiner_graphe(canvas, new_tab)

        # =====================
        # CAS 2 : Fichier texte (.txt) ou Word (.docx)
        # =====================
        elif extension in ['.txt', '.docx']:
            if extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    contenu = f.read()
            else:  # .docx
                doc = Document(file_path)
                contenu = "\n".join([p.text for p in doc.paragraphs])

            text_frame = tk.Frame(new_tab)
            text_frame.pack(expand=1, fill='both')

            text_widget = tk.Text(text_frame, wrap='word')
            scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)

            text_widget.insert('1.0', contenu)
            text_widget.config(state='disabled')

            text_widget.pack(side='left', expand=1, fill='both')
            scrollbar.pack(side='right', fill='y')

        else:
            messagebox.showwarning(
                "Type non pris en charge",
                f"Le fichier '{extension}' n'est pas pris en charge."
            )
            notebook.forget(new_tab)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier : {e}")
        notebook.forget(new_tab)

# Fonction pour enregistrer le fichier actuel
def enregistrer_fichier():
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    if tab_key not in tab_data:
        messagebox.showerror("Erreur", "Aucune donnée disponible pour cet onglet.")
        return

    current_file = tab_data[tab_key].get('fichier')
    
    if current_file:
        try:
            with open(current_file, 'w') as file:
                file.write(sauvegarder_graphe(tab_key))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
    else:
        enregistrer_sous()  # Appelle l'autre fonction si pas encore de fichier associé

# Fonction pour enregistrer sous le fichier actuel
def enregistrer_sous():
    fichier = filedialog.asksaveasfilename(
        defaultextension=".py",
        filetypes=[("Fichiers Python", "*.py")]
    )
    if fichier:
        current_tab = notebook.nametowidget(notebook.select())
        tab_key = str(current_tab)

        if tab_key not in tab_data:
            messagebox.showerror("Erreur", "Aucune donnée disponible pour cet onglet.")
            return

        try:
            with open(fichier, 'w') as file:
                file.write(sauvegarder_graphe(tab_key))
                tab_data[tab_key]['fichier'] = fichier  # Associer le fichier à l'onglet
                notebook.tab(notebook.select(), text=fichier.split('/')[-1])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")

# Fonction pour fermer l'onglet actuel
def fermer_fichier():
    global current_file
    selected = notebook.select()
    if not selected:
        messagebox.showwarning("Avertissement", "Aucun onglet sélectionné à fermer.")
        return

    try:
        current_tab = notebook.nametowidget(selected)
    except Exception:
        # Fallback: try to forget by the selected id
        try:
            notebook.forget(selected)
            messagebox.showinfo("Info", "Onglet fermé.")
        except Exception:
            messagebox.showwarning("Avertissement", "Impossible de déterminer l'onglet à fermer.")
        return

    tab_key = str(current_tab)
    data = tab_data.get(tab_key, {})

    # Vérifiez et nettoyer les frames associés si présents
    try:
        if data and data.get('matrice_adj_frame') is not None:
            for widget in data['matrice_adj_frame'].winfo_children():
                widget.destroy()
    except Exception:
        pass

    # Fermer l'onglet actuel
    try:
        notebook.forget(current_tab)
    except Exception:
        try:
            notebook.forget(selected)
        except Exception:
            pass

    # Supprimer les données associées à l'onglet fermé pour éviter les références
    if tab_key in tab_data:
        try:
            del tab_data[tab_key]
        except Exception:
            pass

    # Si l'onglet fermé correspondait au fichier courant, réinitialiser
    if current_file and data and data.get('fichier') == current_file:
        current_file = None

    messagebox.showinfo("Info", "Onglet fermé avec succès.")

# Fonction pour quitter l'application
def quitter_application():
    confirmation = messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?")
    if confirmation:
        fenetre.quit()

#Fonction pour nettoyer les frames
def effacer_affichages(tab_key, garder=None):
    """Cache les autres affichages et garde uniquement : 'matrices', 'chaines' ou 'parcours'."""
    # Résolution robuste de la clé/tab pour tolérer différentes formes (str(widget), notebook.select(), etc.)
    data = None
    # 1) tentative directe
    try:
        data = tab_data.get(tab_key)
    except Exception:
        data = None

    # 2) si pas trouvé, essayer avec l'identifiant renvoyé par notebook.select()
    if data is None:
        try:
            sel = notebook.select()
            data = tab_data.get(sel)
        except Exception:
            data = None

    # 3) si toujours pas trouvé, tenter de convertir tab_key en widget via nametowidget
    if data is None:
        try:
            widget = notebook.nametowidget(tab_key)
            data = tab_data.get(str(widget))
        except Exception:
            data = None

    # 4) essayer avec le widget actuellement sélectionné
    if data is None:
        try:
            current_widget = notebook.nametowidget(notebook.select())
            data = tab_data.get(str(current_widget)) or tab_data.get(notebook.select())
        except Exception:
            data = None

    # 5) fallback: rechercher une entrée dont le canvas appartient au widget courant
    if data is None:
        try:
            current_widget = notebook.nametowidget(notebook.select())
            for k, v in tab_data.items():
                try:
                    if 'canvas' in v and v['canvas'] is not None:
                        # comparer widgets ou canvas wrappers
                        if getattr(v['canvas'], 'master', None) == current_widget or v['canvas'] == current_widget:
                            data = v
                            break
                except Exception:
                    continue
        except Exception:
            pass

    if data is None:
        # Rien trouvé : informer et sortir proprement
        messagebox.showwarning("Avertissement", "Impossible de trouver les données associées à l'onglet courant.")
        return

    # S'assurer que le frame 'chaine_frame' existe et est valide. Si non, tenter de le recréer
    def ensure_chaine_frame():
        if 'chaine_frame' in data and getattr(data['chaine_frame'], 'winfo_exists', lambda: 0)():
            return
        # essayer de retrouver un parent logique (info frame si disponible)
        parent = None
        if 'matrice_adj_frame' in data and getattr(data['matrice_adj_frame'], 'master', None):
            parent = data['matrice_adj_frame'].master
        elif 'canvas' in data and getattr(data['canvas'], 'master', None):
            parent = data['canvas'].master
        else:
            # fallback: utiliser le widget onglet courant
            try:
                current_tab = notebook.nametowidget(notebook.select())
                parent = current_tab
            except Exception:
                parent = None

        if parent is not None:
            try:
                data['chaine_frame'] = tk.Frame(parent)
            except Exception:
                data['chaine_frame'] = tk.Frame(fenetre)

    ensure_chaine_frame()

    # --- 🔹 MATRICES ---
    try:
        matrice_parent = data['matrice_adj_frame'].master  # parent commun
        if garder == "matrices":
            matrice_parent.pack(side=tk.TOP, pady=5, fill='x')
        else:
            # On vide les contenus mais on garde le frame
            for w in data['matrice_adj_frame'].winfo_children():
                w.destroy()
            for w in data['matrice_inc_frame'].winfo_children():
                w.destroy()
            matrice_parent.pack_forget()
    except Exception:
        pass  # Si les frames n'existent pas encore

    # --- 🔹 CHAINES (Hamilton / Euler) ---
    try:
        if garder == "chaines":
            data['chaine_frame'].pack(side=tk.TOP, pady=10, fill='x')
        else:
            # Effacer les sous-frames s'ils existent
            if 'hamilton_frame' in data and getattr(data['hamilton_frame'], 'winfo_exists', lambda: 0)():
                for w in data['hamilton_frame'].winfo_children():
                    w.destroy()
                data['hamilton_frame'].pack_forget()
            if 'euler_frame' in data and getattr(data['euler_frame'], 'winfo_exists', lambda: 0)():
                for w in data['euler_frame'].winfo_children():
                    w.destroy()
                data['euler_frame'].pack_forget()

            # Si on ne garde pas les parcours, cacher complètement la zone
            if garder != "parcours":
                for w in data['chaine_frame'].winfo_children():
                    w.destroy()
                data['chaine_frame'].pack_forget()
    except Exception:
        pass

    # --- 🔹 PARCOURS (largeur / profondeur) ---
    try:
        if garder == "parcours":
            data['chaine_frame'].pack(side=tk.TOP, pady=10, fill='x')
        else:
            # Ne pas effacer les enfants si l'utilisateur a demandé à garder les 'chaines'
            if garder != "chaines":
                # Supprimer le contenu seulement, garder le frame
                try:
                    for w in data['chaine_frame'].winfo_children():
                        w.destroy()
                except Exception:
                    # Si chaine_frame est invalide, recréer
                    if 'chaine_frame' in data and not getattr(data['chaine_frame'], 'winfo_exists', lambda: 0)():
                        try:
                            current_tab = notebook.nametowidget(notebook.select())
                            data['chaine_frame'] = tk.Frame(current_tab)
                        except Exception:
                            data['chaine_frame'] = tk.Frame(fenetre)
    except Exception:
        pass

# Fonctions pour créer des sommets et des arêtes
def creer_sommet():
    global creation_sommet, creation_arete
    creation_sommet = True
    creation_arete = False

def dessiner_arete(s1, s2, canvas, tab_id=None):
    tab = tab_id or str(canvas.master)
    sommets = tab_data[tab]['sommets']
    x1, y1 = sommets[s1]
    x2, y2 = sommets[s2]
    canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
    # L'étiquette sera dessinée par dessiner_graphe (index cohérent)

def dessiner_arete_orientee(s1, s2, canvas, tab_id=None):
    tab = tab_id or str(canvas.master)
    sommets = tab_data[tab]['sommets']
    x1, y1 = sommets[s1]
    x2, y2 = sommets[s2]
    draw_arrow(canvas, x1, y1, x2, y2)
    # L'étiquette sera dessinée par dessiner_graphe (index cohérent)

# Fonction pour créer une arête orientée
def creer_arete_oriente():
    global creation_sommet, creation_arete
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Vérifier si le type d'arête existant est compatible
    if tab_data[tab_key].get('type_arete') not in [None, 'orientée']:
        messagebox.showerror("Erreur", "Impossible de mélanger arêtes orientées et non orientées dans le même graphe.")
        return

    creation_sommet = False
    creation_arete = True
    tab_data[tab_key]['arete_orientee'] = True
    tab_data[tab_key]['type_arete'] = 'orientée'

# Fonction pour créer une arête non orientée
def creer_arete_non_oriente():
    global creation_sommet, creation_arete
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Vérifier si le type d'arête existant est compatible
    if tab_data[tab_key].get('type_arete') not in [None, 'non orientée']:
        messagebox.showerror("Erreur", "Impossible de mélanger arêtes orientées et non orientées dans le même graphe.")
        return

    creation_sommet = False
    creation_arete = True
    tab_data[tab_key]['arete_orientee'] = False
    tab_data[tab_key]['type_arete'] = 'non orientée'

# Dessiner une arête orientée (flèche)
def draw_arrow(canvas, x1, y1, x2, y2):
    """Dessine une flèche entre deux sommets."""
    # Calculer l'angle de la ligne
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Taille et largeur de la flèche
    arrow_length = 12
    arrow_width = 6
    
    # Rayon d’un sommet
    rayon = 15  # correspond à la taille de ton cercle de sommet
    
    # Calcul des points de départ et d'arrivée (pour ne pas que la flèche entre dans les cercles)
    start_x = x1 + rayon * math.cos(angle)
    start_y = y1 + rayon * math.sin(angle)
    end_x = x2 - rayon * math.cos(angle)
    end_y = y2 - rayon * math.sin(angle)

    # Dessiner la ligne principale
    canvas.create_line(start_x, start_y, end_x, end_y, fill="black", width=2)

    # Coordonnées de la tête de flèche
    x_arrow1 = end_x - arrow_length * math.cos(angle - math.pi / 6)
    y_arrow1 = end_y - arrow_length * math.sin(angle - math.pi / 6)
    x_arrow2 = end_x - arrow_length * math.cos(angle + math.pi / 6)
    y_arrow2 = end_y - arrow_length * math.sin(angle + math.pi / 6)

    # Dessiner la tête
    canvas.create_polygon(end_x, end_y, x_arrow1, y_arrow1, x_arrow2, y_arrow2,
                          fill="black", outline="black")
    
# Fonction pour vérifier si le nouveau sommet est trop proche d'un sommet existant
def sommet_trop_proche(nouveau_sommet, sommets_existants, seuil=20):
    for sx, sy in sommets_existants:
        # Distance correcte avec les puissances
        if math.sqrt((sx - nouveau_sommet[0]) ** 2 + (sy - nouveau_sommet[1]) ** 2) < seuil:
            return True
    return False

def gerer_creation_arete(canvas, tab_key, x, y):
    """
    Gère la création d'une arête (orientée ou non) après sélection des sommets.
    """
    global sommet_selectionne
    data = tab_data[tab_key]
    sommets = data['sommets']

    # Chercher si on a cliqué sur un sommet existant
    for i, (sx, sy) in enumerate(sommets):
        if math.sqrt((sx - x) ** 2 + (sy - y) ** 2) <= 15:  # Clic sur un sommet
            if sommet_selectionne is None:
                # Premier sommet sélectionné
                sommet_selectionne = i
            else:
                # Deuxième sommet : on crée l’arête
                s1 = sommet_selectionne
                s2 = i
                orientee = bool(data.get('arete_orientee', False))

                # Prévenir les doublons
                if orientee:
                    exists = any((e[0] == s1 and e[1] == s2 and e[2]) for e in data['aretes'])
                    if not exists:
                        data['aretes'].append((s1, s2, True))
                else:
                    exists = any((not e[2] and ((e[0] == s1 and e[1] == s2) or (e[0] == s2 and e[1] == s1))) for e in data['aretes'])
                    if not exists:
                        data['aretes'].append((s1, s2, False))

                # Redessiner le graphe pour afficher la nouvelle arête
                dessiner_graphe(canvas, notebook.nametowidget(notebook.select()))
                sommet_selectionne = None  # Réinitialiser
            break

def canvas_click(event, canvas):
    global sommet_selectionne
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)
    data = tab_data[tab_key]
    sommets = data['sommets']

    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    # --- Création d’un sommet ---
    if creation_sommet:
        nouveau_sommet = (x, y)
        if not sommet_trop_proche(nouveau_sommet, sommets):
            sommets.append(nouveau_sommet)
            dessiner_graphe(canvas, current_tab)
        else:
            messagebox.showerror("Erreur", "Le sommet est trop proche d'un autre sommet.")
        return

    # --- Création d’une arête ---
    if creation_arete:
        gerer_creation_arete(canvas, tab_key, x, y)
        return

    # --- Mise à jour du canevas ---
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
    aretes = list(data['aretes'])  # Sauvegarde sous forme de liste pour compatibilité
    graphe_data = f"sommets = {sommets}\naretes = {aretes}\n"
    return graphe_data

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

def surligner_chemin(canvas, sommets, chemin, is_euler=False):
    """Surligne le chemin trouvé sur le canvas avec le tag 'highlight'.
    chemin: pour Hamilton -> liste d'indices [v0, v1, ...]
            pour Euler -> liste de tuples [(u,v), ...]
    """
    try:
        canvas.delete("highlight")
    except Exception:
        pass

    if not chemin:
        return

    # Choisir la couleur selon le type de chaîne : Hamilton -> rouge, Euler -> or/jaune
    highlight_color = "red" if not is_euler else "gold"

    if is_euler:
        for u, v in chemin:
            if u < 0 or v < 0 or u >= len(sommets) or v >= len(sommets):
                continue
            x1, y1 = sommets[u]
            x2, y2 = sommets[v]
            canvas.create_line(x1, y1, x2, y2, fill=highlight_color, width=4, tags=("highlight",))
    else:
        for i in range(len(chemin) - 1):
            u = chemin[i]
            v = chemin[i + 1]
            if u < 0 or v < 0 or u >= len(sommets) or v >= len(sommets):
                continue
            x1, y1 = sommets[u]
            x2, y2 = sommets[v]
            canvas.create_line(x1, y1, x2, y2, fill=highlight_color, width=4, tags=("highlight",))
    # Si l'utilisateur veut des flèches orientées pour les arêtes orientées, dessiner des têtes
    # Note: pour obtenir l'orientation réelle, on cherche dans data['aretes'] si disponible
    try:
        tab = notebook.nametowidget(notebook.select())
        tab_key = str(tab)
        data = tab_data.get(tab_key, {})
        aretes = data.get('aretes')
    except Exception:
        aretes = None

    if aretes:
        # pour Euler: chemin est liste de (u,v)
        if is_euler:
            for u, v in chemin:
                if is_edge_oriented(aretes, u, v):
                    x1, y1 = sommets[u]
                    x2, y2 = sommets[v]
                    _draw_highlighted_arrow(canvas, x1, y1, x2, y2, color=highlight_color)
        else:
            # pour Hamilton: parcours de sommets
            for i in range(len(chemin) - 1):
                u = chemin[i]
                v = chemin[i+1]
                # trouver si arête orientée u->v existe
                if is_edge_oriented(aretes, u, v):
                    x1, y1 = sommets[u]
                    x2, y2 = sommets[v]
                    _draw_highlighted_arrow(canvas, x1, y1, x2, y2, color=highlight_color)

def _draw_highlighted_arrow(canvas, x1, y1, x2, y2, color="red", width=4):
    """Dessine une ligne surlignée avec une tête de flèche (pour arêtes orientées)."""
    # Ligne principale
    canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags=("highlight",))
    # Calculer angle et points pour tête
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_length = 12
    x_arrow1 = x2 - arrow_length * math.cos(angle - math.pi / 6)
    y_arrow1 = y2 - arrow_length * math.sin(angle - math.pi / 6)
    x_arrow2 = x2 - arrow_length * math.cos(angle + math.pi / 6)
    y_arrow2 = y2 - arrow_length * math.sin(angle + math.pi / 6)
    canvas.create_polygon(x2, y2, x_arrow1, y_arrow1, x_arrow2, y_arrow2, fill=color, outline=color, tags=("highlight",))

def is_edge_oriented(aretes, u, v):
    """Retourne True si une arête orientée u->v existe dans la liste aretes."""
    for a, b, orientee in aretes:
        if orientee and a == u and b == v:
            return True
    return False

def show_status(frame, message, fg='red'):
    """Affiche ou met à jour un label de statut dans le frame passé."""
    if frame is None:
        return
    # Supprimer ancien label s'il existe
    try:
        for w in frame.winfo_children():
            if getattr(w, 'is_status_label', False):
                w.destroy()
    except Exception:
        pass
    lbl = tk.Label(frame, text=message, fg=fg, font=("Helvetica", 10, "italic"))
    lbl.is_status_label = True
    lbl.pack(anchor='w', pady=(5, 0))

def afficher_graphe_networkx():
    # Ouvrir un fichier .py ou .txt
    file_path = filedialog.askopenfilename(
        title="Choisir un fichier graphe",
        filetypes=[("Fichiers Python", "*.py"), ("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
    )
    if not file_path:
        return  # L'utilisateur a annulé

    try:
        with open(file_path, "r") as f:
            content = f.read()

        parsed = {}
        exec(content, {}, parsed)  # Exécuter dans un dict séparé

        sommets = parsed.get("sommets", [])
        aretes = parsed.get("aretes", [])

        if not sommets:
            messagebox.showerror("Erreur", "Le fichier ne contient pas de sommets valides.")
            return

        # Déterminer si le graphe est orienté
        orientee = any(edge[2] for edge in aretes if len(edge) > 2)

        G = nx.DiGraph() if orientee else nx.Graph()

        for i in range(len(sommets)):
            G.add_node(i)

        for s1, s2, _ in aretes:
            G.add_edge(s1, s2)

        pos = {i: (x, -y) for i, (x, y) in enumerate(sommets)}
        labels = {i: str(i + 1) for i in G.nodes()}

        # Créer un NOUVEL onglet pour afficher le graphe et lui donner le nom du fichier
        new_tab = tk.Frame(notebook)
        notebook.add(new_tab, text=os.path.basename(file_path))
        notebook.select(new_tab)

        # On crée un frame pour le graphe dans le nouvel onglet
        frame_graph = tk.Frame(new_tab)
        frame_graph.pack(fill=tk.BOTH, expand=True)

        # Créer un frame d'info (parent pour matrices / chaines) similaire à l'UI créée ailleurs
        info_frame = tk.Frame(new_tab)
        info_frame.pack(pady=10, fill='x')

        # Frame parent pour les matrices (au-dessus)
        matrice_parent = tk.Frame(info_frame)
        matrice_parent.pack(side=tk.TOP, pady=5, fill='x')

        matrice_adj_frame = tk.Frame(matrice_parent)
        matrice_adj_frame.pack(side=tk.LEFT, padx=10)

        matrice_inc_frame = tk.Frame(matrice_parent)
        matrice_inc_frame.pack(side=tk.LEFT, padx=10)

        # Frame des chaînes (en dessous)
        chaine_frame = tk.Frame(info_frame)
        chaine_frame.pack(side=tk.TOP, pady=10, fill='x')

        # Enregistrer des données minimales pour l'onglet
        tab_data[str(new_tab)] = {
            'sommets': sommets,
            'aretes': aretes,
            'arete_orientee': orientee,
            'canvas': None,
            'matrice_adj_frame': matrice_adj_frame,
            'matrice_inc_frame': matrice_inc_frame,
            'chaine_frame': chaine_frame,
            'info_frame': info_frame,
            'matrice_parent': matrice_parent,
            'type_arete': None,
            'fichier': file_path
        }
        # Also store under the notebook's selected id for consistent lookup
        try:
            tab_data[notebook.select()] = tab_data[str(new_tab)]
        except Exception:
            pass

        # Normaliser les arêtes (comme ailleurs dans le code)
        normalized_aretes = []
        for edge in aretes:
            try:
                if len(edge) >= 3:
                    normalized_aretes.append((edge[0], edge[1], bool(edge[2])))
                elif len(edge) == 2:
                    normalized_aretes.append((edge[0], edge[1], False))
            except Exception:
                continue

        tab_data[str(new_tab)]['aretes'] = normalized_aretes

        # Créer un Canvas Tkinter pour dessiner le graphe (compatible avec le reste des fonctions)
        canvas = tk.Canvas(frame_graph, bg='white')
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bind("<Button-1>", lambda event: canvas_click(event, canvas))
        tab_data[str(new_tab)]['canvas'] = canvas

        # Dessiner le graphe en utilisant la fonction existante (sommets fournis par le fichier)
        dessiner_graphe(canvas, new_tab)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{e}")

# Fonction pour générer la matrice d'incidence
def generer_matrice_incidence():
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Nettoyer les autres affichages
    effacer_affichages(tab_key, garder="matrices")

    data = tab_data[tab_key]
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
    tab_key = str(current_tab)

    # Nettoyer les autres affichages
    effacer_affichages(tab_key, garder="matrices")

    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    
    n = len(sommets)
    matrice = [[0] * n for _ in range(n)]

    for s1, s2, orientee in aretes:
        if orientee:
            matrice[s1][s2] = 1
        else:
            matrice[s1][s2] = 1
            matrice[s2][s1] = 1

    for widget in data['matrice_adj_frame'].winfo_children():
        widget.destroy()

    titre = tk.Label(data['matrice_adj_frame'], text="Matrice d'Adjacence", font=('Helvetica', 14, 'bold'))
    titre.grid(row=0, column=0, columnspan=n+1, pady=10)

    for j in range(n):
        label = tk.Label(data['matrice_adj_frame'], text=f"{j+1}", width=10, relief="solid")
        label.grid(row=1, column=j+1)

    for i in range(n):
        label = tk.Label(data['matrice_adj_frame'], text=f"{i+1}", width=10, relief="solid")
        label.grid(row=i+2, column=0)

    for i in range(n):
        for j in range(n):
            label = tk.Label(data['matrice_adj_frame'], text=str(matrice[i][j]), width=10, relief="solid")
            label.grid(row=i+2, column=j+1)
      
def est_valide(sommet, chaine, visites, matrice_adj):
    # Vérifie si le sommet peut être ajouté à la chaîne
    dernier_sommet = chaine[-1]
    if visites[sommet] == 1:  # Si le sommet a déjà été visité
        return False
    if matrice_adj[dernier_sommet][sommet] == 0:  # Si il n'y a pas d'arête entre le dernier sommet et celui-ci
        return False
    return True

def trouver_chaine_hamiltonienne(matrice_adj, n, start=0, end=None):
    """
    Recherche d'une chaîne hamiltonienne commençant par `start` et (optionnellement) terminant par `end`.
    start et end sont des indices 0-based. Si end est None, aucun contrainte de fin n'est appliquée.
    """
    chaine = []
    visites = [0] * n  # 0 pour non-visité, 1 pour visité

    # Commence avec le sommet spécifié
    if start < 0 or start >= n:
        return None
    chaine.append(start)
    visites[start] = 1

    # Tente de construire la chaîne en utilisant le backtracking
    if backtrack(matrice_adj, n, chaine, visites, end):
        return chaine
    else:
        return None

def backtrack(matrice_adj, n, chaine, visites, end=None):
    if len(chaine) == n:  # Si la chaîne contient tous les sommets
        if end is None:
            return True
        # vérifier que la chaîne termine bien par 'end' si précisé
        return chaine[-1] == end

    for sommet in range(n):
        if est_valide(sommet, chaine, visites, matrice_adj):
            chaine.append(sommet)
            visites[sommet] = 1
            if backtrack(matrice_adj, n, chaine, visites, end):  # Appel récursif
                return True
            # Retour en arrière
            chaine.pop()
            visites[sommet] = 0

    return False

def afficher_chaine_hamiltonienne():
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Nettoyer les autres affichages
    effacer_affichages(tab_key, garder="chaines")

    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    chaine_frame = data['chaine_frame']

    # S'assurer que le frame existe et est valide (il peut avoir été détruit si l'onglet a été fermé)
    h_frame = data.get('hamilton_frame')
    if h_frame is None or not getattr(h_frame, 'winfo_exists', lambda: 0)():
        data['hamilton_frame'] = tk.Frame(chaine_frame, bd=1, relief='solid')
        data['hamilton_frame'].pack(side=tk.LEFT, padx=10, pady=5, fill='y', anchor='n')
        h_frame = data['hamilton_frame']
    else:
        try:
            for widget in h_frame.winfo_children():
                widget.destroy()
        except tk.TclError:
            # Si le widget était invalide, recréer proprement
            data['hamilton_frame'] = tk.Frame(chaine_frame, bd=1, relief='solid')
            data['hamilton_frame'].pack(side=tk.LEFT, padx=10, pady=5, fill='y', anchor='n')
            h_frame = data['hamilton_frame']

    n = len(sommets)
    if n == 0:
        tk.Label(h_frame, text="Aucun sommet dans le graphe.", font=("Helvetica", 12)).pack(anchor='w')
        return

    matrice_adj = [[0] * n for _ in range(n)]

    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:
            matrice_adj[s2][s1] = 1

    # Demander à l'utilisateur le sommet de départ et d'arrivée (1-based pour l'utilisateur)
    # On passe parent=current_tab pour s'assurer que la boîte n'apparait pas derrière la fenêtre principale
    start_input = simpledialog.askinteger("Départ", f"Sommet de départ (1..{n}) :", parent=current_tab, minvalue=1, maxvalue=n)
    if start_input is None:
        return
    end_input = simpledialog.askinteger("Arrivée", f"Sommet d'arrivée (1..{n}) :", parent=current_tab, minvalue=1, maxvalue=n)
    if end_input is None:
        return

    start_idx = start_input - 1
    end_idx = end_input - 1

    if start_idx == end_idx:
        messagebox.showerror("Entrée invalide", "Pour une chaîne Hamiltonienne, le sommet de départ ne doit pas être égal au sommet d'arrivée.")
        return

    chaine = trouver_chaine_hamiltonienne(matrice_adj, n, start=start_idx, end=end_idx)

    title_label = tk.Label(h_frame, text="Chaîne Hamiltonienne", font=("Helvetica", 12, "bold"))
    title_label.pack(pady=(0,5))
    
    # Redessiner le graphe et surligner le chemin si trouvé
    canvas = data.get('canvas')
    if canvas:
        dessiner_graphe(canvas, current_tab)
        if chaine:
            # si une liste d'arêtes est disponible, la passer pour pouvoir dessiner des flèches
            surligner_chemin(canvas, sommets, chaine, is_euler=False)

    if chaine:
        tk.Label(h_frame, text=" -> ".join([f"{i+1}" for i in chaine]), font=("Helvetica", 12)).pack(anchor='w')
    else:
        tk.Label(h_frame, text="Aucune chaîne Hamiltonienne trouvée.", font=("Helvetica", 12)).pack(anchor='w')
        show_status(h_frame, "Aucune chaîne Hamiltonienne trouvée avec les contraintes fournies.")

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

def trouver_chaine_eulerienne(matrice_adj, n, start=None, end=None):
    """
    Trouve une chaîne eulérienne (liste de paires (u,v)).
    Si start et end sont fournis (indices 0-based), on force le départ/arrivée.
    """
    degrees = [sum(matrice_adj[i]) for i in range(n)]
    impairs = [i for i, d in enumerate(degrees) if d % 2 != 0]

    # Vérifier la condition de parité en fonction des contraintes start/end
    if start is not None and end is not None:
        if start == end:
            # Pour un circuit (départ==arrivée), il faut 0 sommets de degré impair
            if len(impairs) != 0:
                return None
        else:
            # Pour un chemin avec deux extrémités distinctes, les impairs doivent être exactement {start, end}
            if sorted(impairs) != sorted([start, end]):
                return None
    else:
        if len(impairs) not in [0, 2]:
            return None  # Pas de chaîne eulérienne possible

    if not est_connexe(matrice_adj, n):
        return None

    # Choisir le sommet de départ
    if start is not None:
        sommet_de_depart = start
    else:
        sommet_de_depart = impairs[0] if len(impairs) == 2 else 0

    # Copier la matrice pour modification
    mat = [row[:] for row in matrice_adj]

    chaine = []
    def fleury(matrice, sommet):
        for voisin in range(n):
            if matrice[sommet][voisin] == 1:
                supprimer_arete(matrice, sommet, voisin)
                chaine.append((sommet, voisin))
                fleury(matrice, voisin)

    fleury(mat, sommet_de_depart)

    # Si end est donné, vérifier que la dernière arête arrive bien à end (s'il y a des arêtes)
    if end is not None and chaine:
        if chaine[-1][1] != end:
            # Peut être qu'on a trouvé un parcours mais pas se terminant sur end
            return None

    return chaine

# Fonction pour afficher la chaîne eulérienne
def afficher_chaine_eulerienne():
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)

    # Nettoyer les autres affichages
    effacer_affichages(tab_key, garder="chaines")

    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']
    chaine_frame = data['chaine_frame']

    # S'assurer que le frame existe et est valide
    e_frame = data.get('euler_frame')
    if e_frame is None or not getattr(e_frame, 'winfo_exists', lambda: 0)():
        data['euler_frame'] = tk.Frame(chaine_frame, bd=1, relief='solid')
        data['euler_frame'].pack(side=tk.LEFT, padx=10, pady=5, fill='y', anchor='n')
        e_frame = data['euler_frame']
    else:
        try:
            for widget in e_frame.winfo_children():
                widget.destroy()
        except tk.TclError:
            data['euler_frame'] = tk.Frame(chaine_frame, bd=1, relief='solid')
            data['euler_frame'].pack(side=tk.LEFT, padx=10, pady=5, fill='y', anchor='n')
            e_frame = data['euler_frame']

    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]

    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:
            matrice_adj[s2][s1] = 1

    # Demander à l'utilisateur le sommet de départ et d'arrivée (1-based pour l'utilisateur)
    start_input = simpledialog.askinteger("Départ", f"Sommet de départ (1..{n}) :", parent=current_tab, minvalue=1, maxvalue=n)
    if start_input is None:
        return
    end_input = simpledialog.askinteger("Arrivée", f"Sommet d'arrivée (1..{n}) :", parent=current_tab, minvalue=1, maxvalue=n)
    if end_input is None:
        return

    start_idx = start_input - 1
    end_idx = end_input - 1

    # Vérifications préalables et messages explicites
    degrees = [sum(matrice_adj[i]) for i in range(n)]
    impairs = [i for i, d in enumerate(degrees) if d % 2 != 0]

    if not est_connexe(matrice_adj, n):
        messagebox.showerror("Entrée invalide", "Le graphe n'est pas connexe : il est impossible d'obtenir une chaîne eulérienne couvrant toutes les arêtes.")
        return

    # Cas circuit (start==end) : tous les degrés doivent être pairs
    if start_idx == end_idx:
        if len(impairs) != 0:
            messagebox.showerror("Entrée invalide", "Vous avez demandé un circuit (départ == arrivée). Pour cela, tous les sommets doivent avoir un degré pair.")
            return
    else:
        # chemin ouvert : les deux extrémités doivent être les deux sommets de degré impair
        if len(impairs) != 2 or sorted(impairs) != sorted([start_idx, end_idx]):
            messagebox.showerror("Entrée invalide", f"Pour un chemin eulérien ouvert, il doit y avoir exactement deux sommets de degré impair correspondant aux extrémités. Sommets impairs actuels: {[i+1 for i in impairs]}")
            return

    chaine = trouver_chaine_eulerienne(matrice_adj, n, start=start_idx, end=end_idx)

    title_label = tk.Label(e_frame, text="Chaîne Eulérienne", font=("Helvetica", 12, "bold"))
    title_label.pack(pady=(0,5))

    # Redessiner le graphe et surligner la chaîne si trouvée
    canvas = data.get('canvas')
    if canvas:
        dessiner_graphe(canvas, current_tab)
        if chaine:
            # Pour Euler, on a une liste de paires (u,v); essayer d'utiliser l'orientation d'origine
            surligner_chemin(canvas, sommets, chaine, is_euler=True)

    if chaine:
        tk.Label(e_frame, text=" -> ".join([f"{u+1}-{v+1}" for u, v in chaine]), font=("Helvetica", 12)).pack(anchor='w')
    else:
        tk.Label(e_frame, text="Aucune chaîne Eulérienne trouvée.", font=("Helvetica", 12)).pack(anchor='w')
        show_status(e_frame, "Aucune chaîne Eulérienne trouvée avec les contraintes fournies.")

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
    tab_key = str(current_tab)
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']

    # --- Étape 1 : effacer tout sauf les parcours ---
    effacer_affichages(tab_key, garder="parcours")

    # --- Étape 2 : vider manuellement le frame parcours pour éviter les résidus ---
    for w in data['chaine_frame'].winfo_children():
        w.destroy()

    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]

    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:
            matrice_adj[s2][s1] = 1

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

    for sommet in range(n):
        if not visite[sommet]:
            bfs_composante(sommet)

    chaine_frame = data['chaine_frame']
    chaine_frame.pack(side=tk.TOP, pady=10, fill='x')

    canvas = tk.Canvas(chaine_frame, width=700, height=400, bg='white')
    canvas.pack(pady=10)
    dessiner_arbre_couvrant(canvas, arbre, sommets)

    label = tk.Label(
        chaine_frame,
        text="Parcours en largeur : " + " → ".join([f"{i+1}" for i in parcours]),
        font=("Helvetica", 12),
        fg="blue"
    )
    label.pack(padx=10, pady=5)

def parcours_profondeur():
    current_tab = notebook.nametowidget(notebook.select())
    tab_key = str(current_tab)
    data = tab_data[tab_key]
    sommets = data['sommets']
    aretes = data['aretes']

    # --- Étape 1 : effacer tout sauf les parcours ---
    effacer_affichages(tab_key, garder="parcours")

    # --- Étape 2 : vider manuellement le frame parcours ---
    for w in data['chaine_frame'].winfo_children():
        w.destroy()

    n = len(sommets)
    matrice_adj = [[0] * n for _ in range(n)]

    for s1, s2, orientee in aretes:
        matrice_adj[s1][s2] = 1
        if not orientee:
            matrice_adj[s2][s1] = 1

    visite = [False] * n
    parcours = []
    arbre = []

    def dfs(sommet):
        visite[sommet] = True
        parcours.append(sommet)
        for voisin in range(n):
            if matrice_adj[sommet][voisin] == 1 and not visite[voisin]:
                arbre.append((sommet, voisin))
                dfs(voisin)

    for sommet in range(n):
        if not visite[sommet]:
            dfs(sommet)

    chaine_frame = data['chaine_frame']
    chaine_frame.pack(side=tk.TOP, pady=10, fill='x')

    canvas = tk.Canvas(chaine_frame, width=700, height=400, bg='white')
    canvas.pack(pady=10)
    dessiner_arbre_couvrant(canvas, arbre, sommets)

    label = tk.Label(
        chaine_frame,
        text="Parcours en profondeur : " + " → ".join([f"{i+1}" for i in parcours]),
        font=("Helvetica", 12),
        fg="green"
    )
    label.pack(padx=10, pady=5)

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
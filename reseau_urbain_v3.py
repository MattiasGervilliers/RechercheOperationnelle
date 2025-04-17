import random
import math
import networkx as nx
import matplotlib.pyplot as plt
import pprint
import matplotlib.patches as patches

def create_square(side, current_square):
    """
    Crée un nouveau carré à partir d'un carré existant en fonction du côté spécifié.
    """
    y1_raw, y2_raw = current_square[2], current_square[3]
    y_low, y_high = min(y1_raw, y2_raw), max(y1_raw, y2_raw)
    x1_raw, x2_raw = current_square[0], current_square[1]
    x_low, x_high = min(x1_raw, x2_raw), max(x1_raw, x2_raw)

    lx = abs(x_low - x_high) # Largeur du carré existant
    ly = abs(y_low - y_high) # Hauteur du carré existant

    pas_x = max(1,lx//2)
    pas_y = max(1,ly//2)
    # On determine les coordonnées du nouveau carré en fonction du côté choisis
    if side == 'gauche' :
        x1 = x_low
        x2 = x1 + random.randrange(1,lx//pas_x+1)
        y1 = random.randrange(y_low, y_high)
        y2 = y1 + random.randrange(1,ly//pas_y+1)
    elif side == 'droite' :
        x2 = x_high
        x1 = x2 - random.randrange(1,lx//pas_x+1)
        y1 = random.randrange(y_low, y_high)
        y2 = y1 + random.randrange(1,ly//pas_y+1)
    elif side == 'haut':
        y2 = y_high
        y1 = y2 - random.randrange(1,ly//pas_y+1)
        x1 = random.randrange(x_low, x_high)
        x2 = y1 + random.randrange(1,lx//pas_x+1)
    elif side == 'bas':
        y1 = y_low
        y2 = y1 + random.randrange(1,ly//pas_y+1)
        x1 = random.randrange(x_low, x_high)
        x2 = y1 + random.randrange(1,lx//pas_x+1)

    return x1, x2, y1, y2

def create_city_update_neighbours(squares,data, level):
    new_cities = []

    for square in squares:
        #Creer une ville à l'intérieur du carré
        x1, x2, y1, y2 = square
        x_low, x_high = min(x1, x2), max(x1, x2)
        y_low, y_high = min(y1, y2), max(y1, y2)
        x = random.randint(x_low, x_high)
        y = random.randint(y_low, y_high)
        #On ajoute la ville à la liste des villes
        data[len(data)] = {'neighbours': {}, 'x': x, 'y': y, 'cluster': level, 'parent_square': square}
        new_cities.append(len(data)-1) # On garde l'index de la ville créée

    for city in new_cities:
        # On determine le nombre de route qui partent de la ville
        degres = random.randint(1, min(5, len(new_cities) - 1))
        for _ in range(degres):
            neighbour = random.choice(new_cities)
            new_cities.remove(neighbour)
            # On ajoute la ville voisine à la liste des voisins de la ville
            poids = int(math.sqrt((data[city]['x'] - data[neighbour]['x']) ** 2 + (data[city]['y'] - data[neighbour]['y']) ** 2))
            data[city]['neighbours'][neighbour] = [poids]

    return data  

def urban_network(base_square,min_squares_by_side, max_squares_by_side, max_squares, squares=None, data=None, level=0):

    # Si la liste n'est pas définie, on l'initialise
    if squares is None: squares = []
    if data is None:data = {0: {'neighbours': {}, 'x': 0, 'y': 0, 'cluster': 0, 'parent_square': base_square}}
    if level is None:level = 0
    # Si on a ateint le nombre maximum de carrés, on retourne la liste
    if len(squares) >= max_squares: return squares
    # Liste des directions possibles pour créer un carré
    sides = ['gauche', 'droite', 'haut', 'bas']
    
    new_squares = []

    for side in sides:
        # Pour chaque coté du carré, on determine le nombre de sous-carrés à créer
        how_much_new_squares = random.randint(min_squares_by_side,max_squares_by_side)
        # Pour chaque sous-carré, Si on a pas atteint le nombre maximum de carrés, on en crée un nouveau
        for _ in range(how_much_new_squares):
            if len(squares) >= max_squares: break
            new_square = create_square(side, base_square)
            squares.append(new_square)
            new_squares.append(new_square)
        
    # On creer les villes à l'intérieur de chaque sous-carré, et on les relies
    data = create_city_update_neighbours(new_squares,data, level)
    level += 1

    # Une fois que tous les sous-carrés sont créés
    for new_square in new_squares:
        #On rappelle la fonction pour chaque sous-carré, pour créer d'autres sous-carrés etc...
        urban_network(new_square,min_squares_by_side, max_squares_by_side,max_squares, squares, data, level)

    return data

def display_city_graph(data, base_node_size=100):
    """
    Affiche le graphe des villes en coloriant chaque groupe de villes
    issues du même sous-carré avec une couleur différente.
    """
    G = nx.Graph()
    pos = {}
    parent_sq = {}

    # Construire le graphe et collecter positions & parent_square
    for vid, attrs in data.items():
        G.add_node(vid)
        pos[vid] = (attrs['x'], attrs['y'])
        parent_sq[vid] = tuple(attrs['parent_square'])

    for vid, attrs in data.items():
        for neigh, w in attrs['neighbours'].items():
            G.add_edge(vid, neigh, weight=w[0])

    # Regrouper les nœuds par sous-carré
    groups = {}
    for vid, sq in parent_sq.items():
        groups.setdefault(sq, []).append(vid)

    # Assigner une couleur par sous-carré
    keys = list(groups.keys())
    N = len(keys)
    cmap = plt.cm.get_cmap('tab20')
    color_map = {keys[i]: cmap(i / N) for i in range(N)}
    node_colors = [color_map[parent_sq[vid]] for vid in G.nodes()]

    # Tracé
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.axis('equal')
    plt.xlabel("Axe X")
    plt.ylabel("Axe Y")
    plt.title("Villes colorées par sous-carré d'appartenance")
    plt.show()

base_square = (-200,200,-200,200) #limite à ne pas dépasser
data = urban_network(base_square,1,4,20)
pprint.pprint(data)
display_city_graph(data)
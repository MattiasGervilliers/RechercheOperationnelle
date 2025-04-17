'''

data = {
    0: {
        neighbours: {
            0: [13, 1],
            1: [5]
        },
        x: 15,
        y: 10,
        cluster : 1
    }
}

On veut en entrée :
- le nombre de sommets --> u
- quel degres pour chaque sommet (intervale) --> [d1,d2]

Algo :
pour chaque sommet :
    calculer le nombre d'arrete
    pour chaque arrete :
        si nb_de_sommet_actuel < u:
            creer l'arrete et le sommet au bout OU on la ratache a un sommet 
            si choix 1 :
                x1,y1 = x,y+[5m,10000m] => coord du nouveau sommet
            si choix 2 :
                choisir sommet dans x1,y1 = x,y+[5m,100m]
                    si il a moins de x arrete :
                        on le rattache
                    sinon :
                        creer un sommet            
'''

import random
import math
import networkx as nx
import matplotlib.pyplot as plt
import pprint

def create_city_near_another(x_origin, y_origin):
    max_distance = 100 #metres
    x_new = x_origin + random.randrange(-max_distance, max_distance)
    y_new = y_origin + random.randrange(-max_distance, max_distance)
    return x_new, y_new

def find_city_near_another(x_origin, y_origin, data, min_max_degres):
    max_distance = 5 #metres
    voisins_possibles = []

    for i in range(len(data)):
        if len(data[i]['neighbours']) >= min_max_degres[1]:
            continue
        x_current, y_current = data[i]['x'], data[i]['y']

        dist = math.sqrt((x_origin - x_current) ** 2 + (y_origin - y_current) ** 2)
        if dist <= max_distance:
            voisins_possibles.append((i, dist))

        voisins_possibles.sort(key=lambda x: x[1])
        return [v[0] for v in voisins_possibles]  # retourne juste les IDs triés par distance

def add_city(index, x, y, data):
    data[index] = {'x':x, 'y':y, 'cluster':0, 'neighbours': {}}
    return data

def add_neighbour(index_current, index_neighbour, data):
    x1, y1 = data[index_current]['x'], data[index_current]['y']
    x2, y2 = data[index_neighbour]['x'], data[index_neighbour]['y']
    poids = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    # Ajout pour le sommet courant
    if index_neighbour in data[index_current]['neighbours']:
        data[index_current]['neighbours'][index_neighbour].append(poids)
    else:
        data[index_current]['neighbours'][index_neighbour] = [poids]

    # Ajout pour le sommet voisin
    if index_current in data[index_neighbour]['neighbours']:
        data[index_neighbour]['neighbours'][index_current].append(poids)
    else:
        data[index_neighbour]['neighbours'][index_current] = [poids]

    return data


def create_urban_network(i, data, nb_of_cities, nb_of_current_cities=0):
    min_max_degres = (1,4)

    if nb_of_current_cities >= nb_of_cities:
        return data

    degres_current = random.randrange(min_max_degres[0], min_max_degres[1])
    
    for j in range(degres_current):
        if nb_of_current_cities <= nb_of_cities:
            create_or_find_city = random.random()
            if create_or_find_city >= 0.3 : #create new city
                x_neighbour, y_neighbour = create_city_near_another(data[i]['x'], data[i]['y'])
                nb_of_current_cities += 1
                data = add_city(nb_of_current_cities, x_neighbour, y_neighbour, data)
                data = add_neighbour(i, nb_of_current_cities, data)
                create_urban_network(nb_of_current_cities, data, nb_of_cities, nb_of_current_cities)
            else : #find a city
                neighbours = find_city_near_another(data[i]['x'], data[i]['y'], data, min_max_degres)
                if neighbours:
                    for neighbour in neighbours:
                        if neighbour not in data[i]['neighbours'] and neighbour != i:
                            data = add_neighbour(i, neighbour, data)
                            break
                else :
                    x_neighbour, y_neighbour = create_city_near_another(data[i]['x'], data[i]['y'])
                    nb_of_current_cities += 1
                    data = add_city(nb_of_current_cities, x_neighbour, y_neighbour, data)
                    data = add_neighbour(i, nb_of_current_cities, data)
                    create_urban_network(nb_of_current_cities, data, nb_of_cities, nb_of_current_cities)
    return data

data = {0 : { 'neighbours' : {}, 'x':0, 'y':0, 'cluster':0, 'distance':0}}
data = create_urban_network(0, data, 20)
pprint.pprint(data)

def convert_data_to_graph(data):
    G = nx.Graph()

    # Étape 1 : Ajouter les nœuds avec attributs
    for node_id, node_data in data.items():
        G.add_node(node_id, x=node_data['x'], y=node_data['y'], cluster=node_data['cluster'])

    # Étape 2 : Ajouter les arêtes avec poids
    for source, node_data in data.items():
        for target, weights in node_data['neighbours'].items():
            # Pour éviter les doublons dans un graphe non orienté
            if G.has_edge(source, target):
                continue
            poids = weights[-1] if isinstance(weights, list) else weights
            G.add_edge(source, target, weight=poids)

    return G

G = convert_data_to_graph(data)

# Affichage console
print("Nombre de sommets :", G.number_of_nodes())
print("Nombre d'arêtes :", G.number_of_edges())

# Création du layout à partir des positions exactes
pos = {node: (G.nodes[node]['x'], G.nodes[node]['y']) for node in G.nodes()}

# Récupération des poids pour affichage
edge_labels = nx.get_edge_attributes(G, 'weight')

# Création du graphe
plt.figure(figsize=(12, 8))

# Respect strict des coordonnées réelles
nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray', node_size=500)
nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in edge_labels.items()})

plt.title("Graphe urbain basé sur les coordonnées x, y")
plt.axis('on')  # Important : n'utilise pas plt.axis('off') si tu veux voir l'échelle
plt.gca().set_aspect('equal', adjustable='box')  # Échelle 1:1 pour respecter les distances réelles
plt.tight_layout()
plt.show()



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import matplotlib.pyplot as plt
import pprint
import math
import matplotlib.cm as cm
import math
import random
import json
import networkx as nx

def is_connected(enriched):
    G = nx.Graph()
    for node_id, attrs in enriched.items():
        G.add_node(node_id)
        for neighbor_id in attrs['neighbours']:
            G.add_edge(node_id, neighbor_id)
    return nx.is_connected(G), G

def build_logical_graph_data(
    data,
    p_hub=0.6,
    hub_dist_thresh=10,
    k_villages=2,
    max_village_dist=None
):
    """
    Enrichit `data` en y ajoutant, pour chaque hub et chaque village :
      - 'cluster' : l'ID du hub d'origine
      - 'neighbours' : dict { voisin_id: [poids,...], ... }
    Params :
      data : {
        hub_id: {
          'x': float, 'y': float,
          'sousVilles': {sv_id: {'x','y'}, …}
        }, …
      }
      p_hub : probabilité de connexion hubs–hubs quand dist < hub_dist_thresh
      hub_dist_thresh : distance max pour relier deux hubs
      k_villages : nombre de plus proches villages à relier
      max_village_dist : distance max pour relier deux villages (None = pas de filtre)
    """
    enriched = {}
    
    # 1) Initialisation des nœuds
    for hub_id, hub in data.items():
        enriched[hub_id] = {'x': hub['x'], 'y': hub['y'],
                            'cluster': hub_id, 'neighbours': {}}
        for sv_id, coord in hub.get('sousVilles', {}).items():
            vid = f"{hub_id}.{sv_id}"
            enriched[vid] = {'x': coord['x'], 'y': coord['y'],
                             'cluster': hub_id, 'neighbours': {}}

    degres_max_hub = 4
    # 2) Connexions hub–hub
    hubs = [n for n in enriched if isinstance(n, int)]
    for i in range(len(hubs)):
        for j in range(i+1, len(hubs)):
            a, b = hubs[i], hubs[j]
            xa, ya = enriched[a]['x'], enriched[a]['y']
            xb, yb = enriched[b]['x'], enriched[b]['y']
            dist = math.hypot(xa-xb, ya-yb)

            # Degrés actuels des hubs
            deg_a = len(enriched[a]['neighbours'])
            deg_b = len(enriched[b]['neighbours'])

            if dist < hub_dist_thresh and random.random() < p_hub:
                if (deg_a >= degres_max_hub or deg_b >= degres_max_hub):
                    continue
                enriched[a]['neighbours'].setdefault(b, []).append(dist)
                enriched[b]['neighbours'].setdefault(a, []).append(dist)

    degres_max_vil = 3
    # 3) Connexion village–hub parent
    for hub_id, hub in data.items():
        for sv_id in hub.get('sousVilles', {}):
            vid = f"{hub_id}.{sv_id}"
            xa, ya = enriched[hub_id]['x'], enriched[hub_id]['y']
            xb, yb = enriched[vid]['x'], enriched[vid]['y']
            dist = math.hypot(xa-xb, ya-yb)

            # Degrés actuels des hubs
            deg_hub = len(enriched[hub_id]['neighbours'])
            deg_vil = len(enriched[vid]['neighbours'])

            if  (deg_hub >= degres_max_hub or deg_vil >= degres_max_vil):
                continue
            
            enriched[hub_id]['neighbours'].setdefault(vid, []).append(dist)
            enriched[vid]['neighbours'].setdefault(hub_id, []).append(dist)

    # 4) Connexion village–village
    villages = [n for n in enriched if isinstance(n, str)]
    for v in villages:
        xv, yv = enriched[v]['x'], enriched[v]['y']
        # distances à tous les autres villages
        dists = []
        for u in villages:
            if u == v: continue
            xu, yu = enriched[u]['x'], enriched[u]['y']
            dist = math.hypot(xv-xu, yv-yu)

            # Degrés actuels des hubs
            deg_a = len(enriched[v]['neighbours'])
            deg_b = len(enriched[u]['neighbours'])

            # si un filtre existe, on ignore les trop lointains
            if  (deg_a >= degres_max_vil or deg_b >= degres_max_vil):
                continue
            dists.append((dist, u))
        dists.sort(key=lambda t: t[0])
        # on ne prend que les k plus proches admissibles
        for dist, u in dists:
            deg_v = len(enriched[v]['neighbours'])
            deg_u = len(enriched[u]['neighbours'])
            if deg_v >= degres_max_vil or deg_u >= degres_max_vil:
                continue
            enriched[v]['neighbours'].setdefault(u, []).append(dist)
            enriched[u]['neighbours'].setdefault(v, []).append(dist)
            if len(enriched[v]['neighbours']) >= degres_max_vil:
                break
    
    #rend le graphe connexe au cas ou il ne l'est pas 
    isConnected, G = is_connected(enriched)
    if not isConnected:
        components = list(nx.connected_components(G))
        if len(components) > 1:
            for i in range(len(components) - 1):
                A = components[i]
                B = components[i + 1]

                # Relier un nœud de A à un nœud de B (le plus proche)
                min_dist = float('inf')
                best_a, best_b = None, None
                for a in A:
                    for b in B:
                        dx = enriched[a]['x'] - enriched[b]['x']
                        dy = enriched[a]['y'] - enriched[b]['y']
                        d = math.hypot(dx, dy)
                        if d < min_dist:
                            min_dist = d
                            best_a, best_b = a, b

                # Connecter manuellement
                enriched[best_a]['neighbours'].setdefault(best_b, []).append(min_dist)
                enriched[best_b]['neighbours'].setdefault(best_a, []).append(min_dist)

    return enriched

def define_cities_regions(data, MIN_X, MAX_X, MIN_Y, MAX_Y, max_iters=10):
    """
    Étend progressivement chaque point pour définir sa « boîte » périphérique
    [x1,x2]×[y1,y2] sans empiéter sur ses voisins. 
    data : dict {id: {'x':…, 'y':…}, …}
    MIN_X, MAX_X, MIN_Y, MAX_Y : bornes du cadre
    """
    # 1) On démarre en disant que chaque point peut occuper tout l'espace
    for i in data:
        data[i]['periph'] = {
            'x1': MIN_X, 'x2': MAX_X,
            'y1': MIN_Y, 'y2': MAX_Y
        }

    # 2) Boucle de réglage fin jusqu'à stabilisation (ou max_iters)
    for _ in range(max_iters):
        changed = False

        # --- Phase X : ajuster les limites gauche/droite en regardant
        # uniquement les voisins qui partagent déjà une hauteur commune
        for i, pt in data.items():
            x_i = pt['x']
            y1_i = pt['periph']['y1']
            y2_i = pt['periph']['y2']

            lefts, rights = [], []
            # pour chaque autre point
            for j, other in data.items():
                if j == i:
                    continue
                # si leurs hauteurs ne se chevauchent pas, on ignore
                y1_j = other['periph']['y1']
                y2_j = other['periph']['y2']
                if y2_i < y1_j or y2_j < y1_i:
                    continue

                # sinon on calcule le milieu en X
                x_j = other['x']
                midpoint = (x_i + x_j) / 2
                if x_j < x_i:
                    lefts.append(midpoint)
                else:
                    rights.append(midpoint)

            # on choisit la plus grande limite à gauche (ou MIN_X)
            x1_new = max(lefts) if lefts else MIN_X
            # et la plus petite à droite (ou MAX_X)
            x2_new = min(rights) if rights else MAX_X

            # si ça a bougé, on note le changement
            old = pt['periph']
            if x1_new != old['x1'] or x2_new != old['x2']:
                changed = True

            # on enregistre les nouvelles bornes
            old['x1'], old['x2'] = x1_new, x2_new

        # --- Phase Y : ajuster les limites bas/haut en ne regardant
        # que les voisins dont les bandes horizontales se recoupent
        for i, pt in data.items():
            y_i = pt['y']
            x1_i = pt['periph']['x1']
            x2_i = pt['periph']['x2']

            lowers, uppers = [], []
            for j, other in data.items():
                if j == i:
                    continue
                # si leurs bandes X ne se recoupent pas, on ignore
                x1_j = other['periph']['x1']
                x2_j = other['periph']['x2']
                if x2_i < x1_j or x2_j < x1_i:
                    continue

                # on calcule le milieu en Y
                y_j = other['y']
                midpoint = (y_i + y_j) / 2
                if y_j < y_i:
                    lowers.append(midpoint)
                else:
                    uppers.append(midpoint)

            # on prend la plus haute des limites basses (ou MIN_Y)
            y1_new = max(lowers) if lowers else MIN_Y
            # et la plus basse des limites hautes (ou MAX_Y)
            y2_new = min(uppers) if uppers else MAX_Y

            old = pt['periph']
            if y1_new != old['y1'] or y2_new != old['y2']:
                changed = True

            old['y1'], old['y2'] = y1_new, y2_new

        # si aucune limite n'a bougé, on arrête tout de suite
        if not changed:
            break

    return data

def display(data, MIN_X, MAX_X, MIN_Y, MAX_Y):
    """
    Affiche :
      - Les hubs principaux (cercles noirs) et leurs ID
      - Les sous‑villes de chaque hub (carrés orange) et leur ID hub.sousID
      - La boîte périphérique de chaque hub (segments bleus/rouges)
    data : dict {
        hub_id: {
            'x': float, 'y': float,
            'periph': {'x1','x2','y1','y2'},
            'sousVilles': {
                sous_id: {'x','y'}, …
            }
        }, …
    }
    """
    plt.figure(figsize=(8, 6))

    # 1) Hubs et leurs étiquettes
    for hub_id, attrs in data.items():
        x, y = attrs['x'], attrs['y']
        plt.scatter(x, y, marker='o', color='black',
                    label='Hub' if hub_id == 0 else "")
        plt.text(x, y, str(hub_id), fontsize=9, ha='right', va='bottom')

    # 2) Sous‑villes pour chaque hub
    for hub_id, attrs in data.items():
        for sv_id, coord in attrs.get('sousVilles', {}).items():
            x_s, y_s = coord['x'], coord['y']
            plt.scatter(x_s, y_s, marker='s', color='orange',
                        label='Sous‑ville' if (hub_id == 0 and sv_id == 0) else "")
            plt.text(x_s, y_s, f"{hub_id}.{sv_id}",
                     fontsize=7, ha='left', va='bottom')

    # 3) Boîtes périphériques (x1,x2,y1,y2) pour chaque hub
    for hub_id, attrs in data.items():
        p = attrs['periph']
        x1, x2 = p['x1'], p['x2']
        y1, y2 = p['y1'], p['y2']
        # trait bas et haut
        plt.hlines(y1, x1, x2, colors='blue',   linestyles='--', alpha=0.7)
        plt.hlines(y2, x1, x2, colors='blue',   linestyles='--', alpha=0.7)
        # trait gauche et droite
        plt.vlines(x1, y1, y2, colors='red',    linestyles='--', alpha=0.7)
        plt.vlines(x2, y1, y2, colors='red',    linestyles='--', alpha=0.7)

    # 4) Cadre et légende
    plt.xlim(MIN_X, MAX_X)
    plt.ylim(MIN_Y, MAX_Y)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Hubs, sous‑villes et boîtes périphériques')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_graph_data(data, figsize=(8, 8),
                    base_hub_size=200, base_vill_size=20,
                    size_factor=50):
    """
    Affiche chaque nœud en taille proportionnelle à son nombre d'arêtes (degree).
    - base_hub_size : taille min pour un hub
    - base_vill_size: taille min pour un village
    - size_factor   : taille supplémentaire par arête
    """
    fig, ax = plt.subplots(figsize=figsize)

    # 1) Tracer les arêtes (une seule ligne par paire)
    drawn = set()
    for u, attrs in data.items():
        x1, y1 = attrs['x'], attrs['y']
        for v, weights in attrs['neighbours'].items():
            if (v, u) in drawn:
                continue
            x2, y2 = data[v]['x'], data[v]['y']
            ax.plot([x1, x2], [y1, y2], color='gray', alpha=0.5)
            drawn.add((u, v))

    # 2) Déterminer les clusters et leur couleur
    clusters = sorted({attrs['cluster'] for attrs in data.values()})
    cmap = plt.get_cmap('tab10', len(clusters))
    cluster_color = {c: cmap(i) for i, c in enumerate(clusters)}

    # 3) Tracer les nœuds, avec taille selon le nombre d'arêtes
    for node_id, attrs in data.items():
        x, y = attrs['x'], attrs['y']
        deg = sum(len(w_list) for w_list in attrs['neighbours'].values())
        # Choisir base size selon type
        if isinstance(node_id, int):
            size = base_hub_size + size_factor * deg
            marker = '^'
            label = f'Hub {node_id}'
        else:
            size = base_vill_size + size_factor * deg
            marker = 'o'
            label = None

        color = cluster_color[attrs['cluster']]
        ax.scatter(x, y, s=size, marker=marker,
                   color=color, edgecolor='black',
                   label=label)

        ax.text(x, y, str(node_id), fontsize=8,
                ha='center', va='center', color='white')

    # 4) Finitions
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Graphe logique : taille des nœuds ∝ nombre d’arêtes')
    ax.legend(loc='upper right', fontsize='small', ncol=2)
    ax.grid(True)
    plt.tight_layout()
    plt.show()

def generate_sub_cities(data,nb_max_ville, surface_max):
    """
    centre (center_x,center_y), rayon max max_radius,
    n_points : nombre de points,
    rate : paramètre de décroissance exponentielle (plus grand → plus concentré).
    """

    rate = 1 - nb_max_ville // 100
    all_cities = 0

    for _, city in data.items():
        min_x = city['periph']['x1']
        max_x = city['periph']['x2']
        min_y = city['periph']['y1']
        max_y = city['periph']['y2']
        center_x = city['x']
        center_y = city['y']
        all_cities += 1

        nb_min_ville = nb_max_sub_cities_per_city//2
        surface = (max_x - min_x) * (max_y - min_y)
        howBig = surface / surface_max * 100
        nb = int(4 * howBig)
        if nb > nb_max_ville:
            nb_max_ville = nb_max_ville
        n_points = random.randrange(nb_min_ville, nb_max_ville)

       # Calcul des demi-axes
        rx = max(center_x - min_x, max_x - center_x)
        ry = max(center_y - min_y, min_y - center_y)

        city.setdefault('sousVilles', {})

        for i in range(n_points):
            theta = random.uniform(0, 2*math.pi)
            # distance normale dans [0,∞), on tronque à 1 pour rester dans l'ellipse
            d = random.expovariate(rate)
            d = min(d, 1.0)
            # projection dans l’ellipse
            x = center_x + rx * d * math.cos(theta)
            y = center_y + ry * d * math.sin(theta)

            all_cities += 1
            city['sousVilles'][i] = {'x': x, 'y': y}
    
    return data, all_cities

def generate_cities(MIN_X, MAX_X, MIN_Y, MAX_Y, nb_villes):
    # Génération des coordonnées aléatoires
    xs = [random.uniform(MIN_X, MAX_X) for _ in range(nb_villes)]
    ys = [random.uniform(MIN_Y, MAX_Y) for _ in range(nb_villes)]

    data = {i : {'x': xs[i], 'y': ys[i]} for i in range(nb_villes)}

    return data

def main(nb_cities, nb_max_sub_cities_per_city, MIN_X, MAX_X, MIN_Y, MAX_Y, display_regions, display_graph, display_console, save_json):
    
    surface_max = MAX_X * MAX_Y

    data = generate_cities(MIN_X, MAX_X, MIN_Y, MAX_Y, nb_cities)
    data = define_cities_regions(data, MIN_X, MAX_X, MIN_Y, MAX_Y)
    data, all_cities = generate_sub_cities(data,nb_max_sub_cities_per_city, surface_max)
    
    if display_regions:
        display(data, MIN_X, MAX_X, MIN_Y, MAX_Y)
    
    if display_console or display_graph or save_json:
        data_final = build_logical_graph_data(data, max_village_dist=surface_max/8)
    
    if display_console:
        pprint.pprint(data_final)

    if save_json:
        with open(f'urbain_network_{all_cities}_cities.json', 'w', encoding='utf-8') as f:
            json.dump(data_final, f, ensure_ascii=False, indent=2)
       
    if display_graph:
        plot_graph_data(data_final)

if __name__ == "__main__":

    nb_cities = 10 # Nombre de hubs
    nb_max_sub_cities_per_city = 30
    MIN_X, MAX_X, MIN_Y, MAX_Y = 0, 10, 0, 10 #cadre

    display_regions = False
    display_graph = True
    display_console = False
    save_json = True

    main(nb_cities, nb_max_sub_cities_per_city, MIN_X, MAX_X, MIN_Y, MAX_Y, display_regions, display_graph, display_console, save_json)
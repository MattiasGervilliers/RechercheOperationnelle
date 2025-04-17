#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import matplotlib.pyplot as plt
import pprint

def main():
    # Nombre de points et dimensions du cadre
    hub = 5
    hub_x1, hub_x2, hub_y1, hub_y2 = 0, 10, 0, 10

    # Génération des coordonnées aléatoires
    xs = [random.uniform(hub_x1, hub_x2) for _ in range(hub)]
    ys = [random.uniform(hub_y1, hub_y2) for _ in range(hub)]

    hubs = {i : {'x': xs[i], 'y': ys[i]} for i in range(hub)}

    # Création de la périphérie de la ville
    """hubs_periph = {}
    for point in hubs_id_sorted:

        max_expension = hub_x2//2
        pas = hub_x2//10
        hubs_periph[point] = {'periph' : {'x1':None, 'x2':None, 'y1':None, 'y2':None}}
 
        #expansion vers la gauche
        x1 = hubs[point]['x']
        expansion = 0
        objectTouched = False
        while not objectTouched:
            x1 = x1 -pas
            expansion += pas

            if x1 <= hub_x1 : #Si on touche le bord
                hubs_periph[point]['periph']['x1'] = hub_x1
                objectTouched = True 

            if expansion >= max_expension:
                hubs_periph[point]['periph']['x1'] = x1
                objectTouched = True

            for point_periph in hubs_periph:
                if point_periph != point and hubs_periph[point_periph]['periph']['x2']: 
                    x2_voisin = hubs_periph[point_periph]['periph']['x2']
                    if x1 <= x2_voisin :
                        hubs_periph[point]['periph']['x1'] = x1
                        objectTouched = True #Si on touche le bord

        #expansion vers la droite
        x2 = hubs[point]['x']
        expansion = 0
        objectTouched = False
        while not objectTouched and expansion < max_expension:
            x2 = x2 +pas
            expansion += pas

            if x2 >= hub_x2 : #Si on touche le bord
                hubs_periph[point]['periph']['x2'] = hub_x2
                objectTouched = True 
            
            if expansion >= max_expension:
                hubs_periph[point]['periph']['x2'] = x2
                objectTouched = True

            for point_periph in hubs_periph:
                if point_periph != point and hubs_periph[point_periph]['periph']['x1']: 
                    
                    x1_voisin = hubs_periph[point_periph]['periph']['x1']
                    if x2 >= x1_voisin :
                        hubs_periph[point]['periph']['x2'] = x2
                        objectTouched = True #Si on touche le bord
    """
    
    #Création de la limite à gauche -> milieu entre x_current et x-1
    hubs_periph = {}
    hubs_id_sorted = sorted(hubs.items(), key=lambda item: item[1]['x'])
    hubs_id_sorted = [idx for idx, _ in hubs_id_sorted]

    medians = []
    for i in range(len(hubs_id_sorted) - 1):
        a, b = hubs_id_sorted[i], hubs_id_sorted[i + 1] # On récupère les deux hubs consécutifs
        midpoint = (xs[a] + xs[b]) / 2 # On calcule le milieu
        medians.append(midpoint) # On l’ajoute à la liste

    # Construction des limites
    for k, hub_id in enumerate(hubs_id_sorted):
        # borne gauche
        if k == 0:
            x1 = hub_x1
        else:
            x1 = medians[k - 1]
        # borne droite
        if k == len(hubs_id_sorted) - 1:
            x2 = hub_x2
        else:
            x2 = medians[k]
        hubs_periph[hub_id] = {'x1': x1, 'x2': x2}

    pprint.pprint(hubs_periph)

    # Affichage
    plt.figure(figsize=(8, 6))
    # vos points et leurs labels
    plt.scatter(xs, ys, marker='o')
    for i, (x, y) in enumerate(zip(xs, ys)):
        plt.text(x, y, str(i), fontsize=9, ha='right', va='bottom')

    # tracer les lignes x1 (rouge) et x2 (vert)
    for hub_id, per in hubs_periph.items():
        plt.axvline(per['x1'], color='red',   linestyle='--', alpha=0.7)
        plt.axvline(per['x2'], color='green', linestyle='--', alpha=0.7)

    plt.xlim(hub_x1, hub_x2)
    plt.ylim(hub_y1, hub_y2)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'{hub} hubs et leurs limites horizontales (x1/x2)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

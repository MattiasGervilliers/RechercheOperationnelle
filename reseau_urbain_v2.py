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

Algo :

je veux :
- placer un carré,
- placer un carré dans un carré
- suivant si les coté du carré sont oui ou non dans le carré d'origine : on fait un autre carré qui a un coté en commun avec l'autre


'''

import random
import math
import networkx as nx
import matplotlib.pyplot as plt
import pprint
import matplotlib.patches as patches

def place_square(x_origin, y_origin, max_range):
    x1 = x_origin + random.randint(-max_range, max_range)
    x2 = x_origin + random.randint(-max_range, max_range)
    y1 = y_origin + random.randint(-max_range, max_range)
    y2 = y_origin + random.randint(-max_range, max_range)
    return min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)

def place_city_in_square(x1, x2, y1, y2):
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    return x, y

def place_square_in_square(x1, x2, y1, y2, where, max_range, min_range):

    if where == 'gauche':
        new_x2 = x1
        new_x1 = new_x2 - random.randint(min_range, max_range)
        new_y1 = random.randint(y1, y2)
        new_y2 = new_y1 + random.randint(min_range, max_range)
    elif where == 'droite':
        new_x1 = x2
        new_x2 = new_x1 + random.randint(min_range, max_range)
        new_y1 = random.randint(y1, y2)
        new_y2 = new_y1 + random.randint(min_range, max_range)
    elif where == 'haut':
        new_y2 = y1
        new_y1 = new_y2 - random.randint(min_range, max_range)
        new_x1 = random.randint(x1, x2)
        new_x2 = new_x1 + random.randint(min_range, max_range)
    elif where == 'bas':
        new_y1 = y2
        new_y2 = new_y1 + random.randint(min_range, max_range)
        new_x1 = random.randint(x1, x2)
        new_x2 = new_x1 + random.randint(min_range, max_range)

    else:
        new_x1, new_x2, new_y1, new_y2 = place_square((x1 + x2)//2, (y1 + y2)//2, max_range)

    return min(new_x1, new_x2), max(new_x1, new_x2), min(new_y1, new_y2), max(new_y1, new_y2)

def place_multiple_square_in_square(n, x1, x2, y1, y2, max_range, min_range, depth):

    squares = []
    expension = 4 #nb de cotés

    def recurse(cur_x1, cur_x2, cur_y1, cur_y2, level, expension):
        nonlocal squares # 
        if level == 0:
            return
        
        if (cur_x1 <= x1 or cur_x2 >= x2 or cur_y1 <= y1 or cur_y2 >= y2):
            return  # le carré touche au bord, on arrête la propagation
        
        sides_in_square = ['gauche', 'droite', 'bas', 'haut']
        sides = []
        sides.append(random.choice(sides_in_square))
        sides_in_square.remove(sides[0])
        sides.append(random.choice(sides_in_square))

        for side in sides:
            new_x1, new_x2, new_y1, new_y2 = place_square_in_square(cur_x1, cur_x2, cur_y1, cur_y2, side, max_range, min_range)
            squares.append((new_x1, new_x2, new_y1, new_y2))

            recurse(new_x1, new_x2, new_y1, new_y2, level - 1, expension)

    # Carré de départ
    start_x1, start_x2, start_y1, start_y2 = place_square((x1 + x2) // 2, (y1 + y2) // 2, max_range)
    squares.append((start_x1, start_x2, start_y1, start_y2))
    recurse(start_x1, start_x2, start_y1, start_y2, depth, expension)

    return squares

# Grand carré
x1, x2, y1, y2 = -150, 150, -150, 160
carres = place_multiple_square_in_square(6, x1, x2, y1, y2, 30,20, 5)
print(carres)
fig, ax = plt.subplots()

# Grand carré en fond
grand_carre = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2, edgecolor='black', facecolor='lightgray')
ax.add_patch(grand_carre)

# Tous les sous-carrés
for (cx1, cx2, cy1, cy2) in carres:
    rect = patches.Rectangle((cx1, cy1), cx2 - cx1, cy2 - cy1, linewidth=1, edgecolor='blue', facecolor='none')
    ax.add_patch(rect)

ax.set_xlim(x1 - 30, x2 + 30)
ax.set_ylim(y1 - 30, y2 + 30)
ax.set_aspect('equal')
plt.title("Carrés successifs avec côtés communs dans un carré principal")
plt.grid(True)
plt.show()

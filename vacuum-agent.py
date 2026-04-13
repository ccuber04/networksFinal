import random
import copy

from jedi.inference.utils import to_tuple

import search
# number of tiles in room
X, Y = 6, 6

# tile status
clean = 0
dirty = 1
def probability(percentage):
    return int(percentage > random.randint(0, 99))

def diffuse(tiles, fill_empty_spots=False):
    new_tiles = [row.copy() for row in tiles]
    for y in range(1, len(tiles)-1):
        for x in range(1, len(tiles[0])-1):
            num_dirty = sum(tiles[y+dy][x+dx] for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if num_dirty >= 5 or (fill_empty_spots and num_dirty == 0):
                new_tiles[y][x] = dirty
            else:
                new_tiles[y][x] = clean

    return new_tiles

def generate_tiles(X, Y, dirty=10):
    tiles = [[probability(dirty) for _ in range(X)] for _ in range(Y)]
    for _ in range(4):
        tiles = diffuse(tiles, True)
    for _ in range(5):
        tiles = diffuse(tiles)
    return to_tuple(tiles)

def to_tuple(tiles):
    return tuple(tuple(row) for row in tiles)

def to_list(tiles):
    return list(list(row) for row in tiles)

def print_tiles(tiles):
    symbols = [' ', '@']
    print('+' + X * '-' + '+')
    for row in tiles:
        print('|', end='')
        for col in row:
            print(symbols[col], end='')
        print('|')
    print('+' + X * '-' + '+')

def print_path(node):
    actions = search.path_actions(node)
    states = search.path_states(node)
    _, positions = zip(*states)
    directions = {(0, 0): 's', (1, 0): '>', (-1, 0): '<', (0, 1): 'v', (0, -1): '^'}
    tiles = to_list(states[0][0])

    for position, action in zip(positions, actions):
        x, y = position
        tiles[y][x] = directions[action]

    last_x, last_y = position
    tiles[last_y][last_x] = 'o'
    print('+' + X * '-' + '+')
    for row in tiles:
        print('|', end='')
        for col in row:
            if col == 0:
                print(' ', end='')
            else:
                print(col, end='')
        print('|')
    print('+' + X * '-' + '+')

def walkable(x, y):
    return x >= 0 and x < X and y >= 0 and y < Y

def is_goal(state):
    tiles, _ = state
    return all(all(r == clean for r in t) for t in tiles)

def actions(state):
    action = []
    tiles, position = state
    x, y = position
    if walkable(x, y):
        if tiles[y][x] == dirty:
            action.append((0, 0))
        for a in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            if walkable(x + a[0], y + a[1]):
                action.append(a)
    return action

def result(state, action):
    tiles, position = state
    t = to_list(tiles)
    x, y = position
    ax, ay = action
    if action == (0, 0):
        t[y][x] = clean
    return to_tuple(t), (x+ax, y+ay)

def action_cost(state, action, new_state):
    if action != (0, 0):
        return 2
    return 1

def total_dirty_tiles(state):
    tiles, position = state
    dirty_tiles = 0
    for tile in tiles:
        if tile == dirty:
            dirty_tiles += 1
    return dirty_tiles

def h(n):
    return total_dirty_tiles(n.state)

# generate a messy room
tiles = generate_tiles(X, Y)

robot_position = (0, 0)  # robot starts in upper left corner
initial = (tiles, robot_position)
problem = search.Problem(initial, is_goal, result, actions, action_cost)
print_tiles(tiles)

# sol = search.uniform_cost_search(problem)
# # print(search.path_actions(sol1))
# print_path(sol)

sol1 = search.astar_search(problem, h)
# print(search.path_actions(sol1))
print_path(sol1)

sol2 = search.greedy_search(problem, h)
# print(search.path_actions(sol2))
print_path(sol2)

sol3 = search.astar_weighted_search(problem, h, w=3)
# print(search.path_actions(sol2))
print_path(sol3)

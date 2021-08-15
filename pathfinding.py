from queue import PriorityQueue
from util import Action

def generate_action_permutations():
    return []

def get_neighbours(tetris_game, node):
    n = []

    # Generate permutations of actions
    for ac in generate_action_permutations():
        n.append(tetris_game.getNextStateFromState(node, ac))
        
    return n

def heuristic(goal, node):
    pass

def find_path(tetris_game, tetromino, current_pos, current_rotation, goal_pos, goal_rotation):
    
    start_state = tetris_game.saveState()   # Might need to remove current tetromino here?

    frontier = PriorityQueue()
    frontier.put(start_state)

    path = {}
    cost = {}
    path[start_state] = None
    cost[start_state] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal_pos:
            break

        for neighbour in get_neighbours(tetris_game, current):
            new_cost = cost[current] + 1    # Cost equal per frame? 
            if neighbour not in cost or new_cost < cost[neighbour]:
                cost[current] = new_cost
                p = new_cost + 2
                frontier.put(neighbour, p)
                path[neighbour] = current
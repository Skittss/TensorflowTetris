from queue import PriorityQueue
from util import Action

def simulate_DAS(actions, currentCharge):
    if not actions[Action.Left] and not actions[Action.Right]:
        currentCharge = 0
        return currentCharge, True

    if currentCharge > 0 and actions[Action.Left] and not actions[Action.Right]:
        currentCharge = 0
        return currentCharge, True

    if currentCharge < 0 and not actions[Action.Left] and actions[Action.Right]:
        currentCharge = 0
        return currentCharge, True

    return currentCharge, False


def heuristic(goal, node):
    pass

def get_neighbours(tetris_game, node):

    DAS = tetris_game.DAS
    DAS_charge = tetris_game.DAScharge

    ARR = tetris_game.ARR
    ARR_tick = tetris_game.ARRframeTick

    das_charge, reset_ARR = simulate_DAS(actions, DAS_charge)


def find_path(tetris_game, tetromino, current_pos, current_rotation, goal_pos, goal_rotation):
    
    frontier = PriorityQueue()
    frontier.put()

    path = {}
    cost = {}
    path[current_pos] = None
    cost[current_pos] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal_pos:
            break

        for neighbour in get_neighbours(current):
            new_cost = cost[current] + 1    # Cost equal per frame? 
            if neighbour not in cost or new_cost < cost[neighbour]:
                cost[current] = new_cost
                p = new_cost + 2
                frontier.put(neighbour, p)
                path[neighbour] = current
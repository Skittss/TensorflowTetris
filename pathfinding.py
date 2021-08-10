from queue import PriorityQueue

def heuristic(goal, node):


def get_neighbours(tetris_game, node):

    DAS = tetris_game.DAS
    DAS_charge = tetris_game.DAScharge

    ARR = tetris_game.ARR
    ARR_tick = tetris_game.ARRframeTick


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
from queue import PriorityQueue
from util import Action, getEmptyActionObj
from tetris import Tetris
from agent_config import AgentGameConfig, AgentHandlingConfig

def action_from_binary(binary):
    # Binary in the form L | R | Rot-L | Rot-R | Rot-F | SoftDrop
    ac = getEmptyActionObj()
    for i in range(len(binary)):
        ac[Action(i)] = binary[i]

    return ac

def generate_action_permutations():

    # L | R | Rot-L | Rot-R | Rot-F
    # ------------------------------
    # 0 | 0 |   0   |   0   |   0
    # 0 | 0 |   0   |   0   |   1
    # 0 | 0 |   0   |   1   |   0
    # 0 | 0 |   0   |   1   |   1
    # 0 | 0 |   1   |   0   |   0
    # 0 | 0 |   1   |   0   |   1
    # 0 | 0 |   1   |   1   |   0
    # 0 | 0 |   1   |   1   |   1
    # 0 | 1 |   0   |   0   |   0
    #    etc...

    # TODO: Save memory here as move binaries are a subset of rotation binaries
    move_direction_binaries = [[int(v) for v in '{0:02b}'.format(n)] for n in range(0, 2**2)]
    rotation_binaries = [[int(v) for v in '{0:03b}'.format(n)] for n in range(0, 2**3)]

    combined_binaries = [move + rotation for move in move_direction_binaries for rotation in rotation_binaries]
    permutations = [action_from_binary(b + [soft_drop]) for soft_drop in range(2) for b in combined_binaries]

    # Final action for choosing to hard drop. (No DAS charge between drops)
    return permutations + [action_from_binary([int(v) for v in '{0:07b}'.format(1)])]

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

    # TODO: Consider what information determines a unique state, is it the entire state? - Quite possibly yes.
    # TODO: More information may be needed to determine if piece is in correct position, i.e. hard drop puts piece in correct position but switches so information about where it was dropped is lost.

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

if __name__ == "__main__":
    game = Tetris(AgentGameConfig, AgentHandlingConfig)
    state = game.saveState()
    [print(i) for i in get_neighbours(game, state)]
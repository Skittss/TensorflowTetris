from queue import PriorityQueue
from util import Action, getEmptyActionObj, actionObjToStr
from tetris import Tetris
from agent_config import AgentGameConfig, AgentHandlingConfig

def init_action_permutations(cls):
    cls.set_action_permutations()
    return cls

@init_action_permutations
class Pathfinder:

    action_permutations = None

    @classmethod
    def set_action_permutations(cls):
        cls.action_permutations = cls.__generate_action_permutations()

    @classmethod
    def __action_from_binary(cls, binary):
        # Binary in the form L | R | Rot-L | Rot-R | Rot-F | SoftDrop
        ac = getEmptyActionObj()
        for i in range(len(binary)):
            ac[Action(i)] = binary[i]

        return ac

    @classmethod
    def __generate_action_permutations(cls):

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
        move_direction_binaries = [[int(v) for v in '{0:02b}'.format(n)] for n in [0] + [2**e for e in range(0, 2)]]
        rotation_binaries = [[int(v) for v in '{0:03b}'.format(n)] for n in [0] + [2**e for e in range(0, 3)]]

        combined_binaries = [move + rotation for move in move_direction_binaries for rotation in rotation_binaries]
        permutations = [cls.__action_from_binary(b + [soft_drop]) for soft_drop in range(2) for b in combined_binaries]

        # Final action for choosing to hard drop. (No DAS charge between drops)
        return permutations + [cls.__action_from_binary([int(v) for v in '{0:07b}'.format(1)])]

    @classmethod
    def __get_action_cost(cls, neighbour, ac):
        
        c = 0
        c += neighbour.deltaRotation
        c += neighbour.deltaPos
        if ac[Action.SoftDrop]:
            c+= 1

        return c

    @classmethod
    def __get_neighbours(cls, tetris_game, node):

        # TODO cull states where piece is below pos and cannot be kicked to make the difference up (by > 2 tiles?)

        if node.justDroppedTo:
            return []

        n = []

        # Generate permutations of actions
        for ac in cls.action_permutations:
            n.append((tetris_game.getNextStateFromState(node, ac), ac))
            
        return n

    @classmethod
    def __heuristic(cls, goal, node):

        (goal_pos_x, goal_pos_y), goal_rotate_state = goal

        if node.justDroppedTo:
            (pos_x, pos_y), r = node.justDroppedTo

        else:
            pos = node.currentTetrominoState[3]
            pos_x, pos_y = pos[0, 0], pos[0, 1]
            r = node.currentTetrominoState[4]
            harddrop_pos_x, harddrop_pos_y = node.currentHardDropPosition

            if goal_pos_x == harddrop_pos_x and goal_pos_y == harddrop_pos_y and r == goal_rotate_state:
                return 0

        manhattan_distance = abs(goal_pos_x - pos_x) + abs(goal_pos_y - pos_y)
        rotation_difference = abs(goal_rotate_state - r)

        return manhattan_distance + rotation_difference

    @classmethod
    def __state_hit_goal_state(cls, goal, node):

        # Check if the piece was dropped into the goal position
        if node.justDroppedTo:
            # TODO: Ensure piecewise comparison is correct here.
            return goal == node.justDroppedTo

        pos = node.currentTetrominoState[3]
        rotate_state = node.currentTetrominoState[4]
        (goal_pos_x, goal_pos_y), goal_rotate_state = goal

        return rotate_state == goal_rotate_state and pos[0, 0] == goal_pos_x and pos[0, 1] == goal_pos_y

    @classmethod
    def __construct_path_from_dict(cls, dict, final_state):

        if final_state is None:
            return None

        path = []
        current_node = final_state
        while not dict[current_node] is None:
            print(current_node)
            next_node, ac = dict[current_node]
            path.append(ac)
            current_node = next_node

        return path[::-1]

    @classmethod
    def __find_path(cls, tetris_game, goal_piece_state):

        # TODO: check state is not terminal i.e. no new piece. Make neighbours return empty list for these.
        # TODO: consider garbage offset. I.e. goal does not change but position updates as garbage enters
        
        start_state = tetris_game.saveState()   # Might need to remove current tetromino temporarily here?
        final_state = None

        # TODO Might need to define eq for gamestate as currently two gamestates cannot be equal

        frontier = PriorityQueue()
        frontier.put((0, start_state))

        path = {}
        cost = {}
        path[start_state.reducedTuple()] = None
        cost[start_state.reducedTuple()] = 0

        while not frontier.empty():
            _, current_state = frontier.get()

            if cls.__state_hit_goal_state(goal_piece_state, current_state):

                final_state = current_state.reducedTuple()
                break

            for (neighbour, ac) in cls.__get_neighbours(tetris_game, current_state):

                neighbour_dict_key = neighbour.reducedTuple()

                new_cost = cost[current_state.reducedTuple()] + cls.__get_action_cost(neighbour, ac) + 1
                if neighbour_dict_key not in cost or new_cost < cost[neighbour_dict_key]:
                    cost[neighbour_dict_key] = new_cost
                    h = cls.__heuristic(goal_piece_state, neighbour)
                    p = new_cost + h
                    frontier.put((p, neighbour))
                    path[neighbour_dict_key] = (current_state.reducedTuple(), ac)

                    print(f"Goal: {goal_piece_state}\t | Current: ({current_state.currentTetrominoState[3]}, {current_state.currentTetrominoState[4]})\t | After Ac: ({neighbour.currentTetrominoState[3]}, {neighbour.currentTetrominoState[4]})\t | Cost: {new_cost}\t | Hu: {h}\t | P {p} \t| {actionObjToStr(ac)}")

        return path, final_state

    @classmethod
    def get_path(cls, game, goal):

        return cls.__construct_path_from_dict(*cls.__find_path(game, goal))

if __name__ == "__main__":
    game = Tetris(AgentGameConfig, AgentHandlingConfig)
    [print(actionObjToStr(a)) for a in Pathfinder.action_permutations]
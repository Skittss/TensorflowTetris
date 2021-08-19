# Devise an algorithm to calculate all the possible next *moves*, all information in between is redundant and can be scripted I assume.
# Perhaps brute forcing possible next actions? How can I go about calculating the possible actions?
# A valid piece placement is where pieces do not overlap, and there is a filled square directly below one of the matrix positions. We then have to consider kicks and the use of hold.

# Determine how to place piece
# Deep Q for piece placement.


# Find possible drop locations from the board initially based on any position which leaves a tetromino 1 block above a filled tile on the grid, and with no overlapping.

import numpy as np
from agent_config import AgentGameConfig, AgentHandlingConfig
from tetris import Tetris
from pathfinder import Pathfinder
from util import actionObjToStr, getEmptyActionObj
import random

class PiecePlacementAgent:

    def __init__(self):
        self.path = None
        self.path_idx = 0

    def assign_hook_funcs(self, tetris_game: Tetris):
        tetris_game.nextTetrominoHook = self.get_random_path

    def get_random_path(self, tetris_game: Tetris):
        drop_positions = list(self.get_drop_positions(tetris_game.currentTetromino, tetris_game).keys())
        self.path = None
        if len(drop_positions) > 0:
            while self.path is None:
                idx = random.randint(0, len(drop_positions) - 1)
                pos = drop_positions[idx]
                print(pos)
                self.path = Pathfinder.get_path(tetris_game, pos)
                self.path_idx = 0
                print(f"Path found: {[actionObjToStr(a) for a in self.path] if self.path else None}")
                # if path:
                #     for ac in path:
                #         print(actionObjToStr(ac))

                # else:
                #     print("No path found.")

    def get_action(self):
        if self.path and len(self.path) > self.path_idx:
            ac = self.path[self.path_idx]
            self.path_idx += 1
            return ac

        return getEmptyActionObj()

    def get_bottom_piece_index_in_column(self, matrix, col):
        
        column = matrix[:,col]

        idx, = np.where(column != 0)

        if idx.size > 0:
            return np.max(idx)

        # Should not see this return if used with helper function below.
        return -1

    def get_left_right_non_empty_column_in_matrix(self, matrix):

        # Double while loop... too bad!
        i = -1
        col_empty = True
        while col_empty and i < matrix.shape[1] - 1:
            i += 1
            col_empty = not matrix[:,i].any()
            
        left = i

        i = matrix.shape[1]
        col_empty = True
        while col_empty and i > 0:
            i -= 1
            col_empty = not matrix[:,i].any()

        right = i

        return left, right

    def get_drop_positions(self, tetromino, tetris_game):

        empty_above_tiles = tetris_game.getPositionsOfDropTiles()
        drop_positions = {}

        # Test positions which end with a tile in the tetromino being above each filled tile on the grid
        for (y,x) in empty_above_tiles:

            # Don't bother with rotations for O piece to remove complexity.
            n_rotations = 1 if tetromino.tag == 3 else 4

            # Consider each subsequent rotation of the piece
            for k in range(0, n_rotations):

                _, matrix = tetromino.getRotatedMatrix(k=k)

                left_offset, right_offset = self.get_left_right_non_empty_column_in_matrix(matrix)

                # TODO: check correct order here.
                for i in range(-right_offset, -left_offset + 1):
                    j = self.get_bottom_piece_index_in_column(matrix, -i)

                    # Need to swap x, y as game uses [x, y] for pos.
                    pos = np.array([[x + i, y - j]])
                    # Create a hashable tuple pos for use in dict.
                    tuplePos = (x + i, y - j)

                    already_added = True
                    try:
                        drop_positions[(tuplePos, -k%4)]
                    except KeyError:
                        already_added = False

                    if not already_added:
                        if tetris_game.canPlaceOnGrid(matrix, pos):
                            drop_positions[(tuplePos, -k%4)] = True
        
        return drop_positions

if __name__ == "__main__":

    test = PiecePlacementAgent()
    tetris = Tetris(AgentGameConfig, AgentHandlingConfig)
    # tetris.grid[35:40, :] = np.array([
    #     [1,1,0,0,0,0,0,0,0,0],
    #     [1,0,0,0,0,0,0,0,0,0],
    #     [1,0,1,1,1,1,1,1,1,1],
    #     [1,0,0,1,1,1,1,1,1,1],
    #     [1,0,1,1,1,1,1,1,1,1]
    # ]) #(0, 37), 1, kicked from (1, 35), 0
    dropPos = list(test.get_drop_positions(tetris.currentTetromino, tetris).keys())
    print(dropPos)

    for pos in dropPos:
        path = Pathfinder.get_path(tetris, pos)
        if path:
            for ac in path:
                print(actionObjToStr(ac))

        else:
            print("No path found.")
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
from util import actionObjToStr

class PiecePlacementAgent:

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
                        drop_positions[(tuplePos, k)]
                    except KeyError:
                        already_added = False

                    if not already_added:
                        if tetris_game.canPlaceOnGrid(matrix, pos):
                            drop_positions[(tuplePos, k)] = True
        
        return drop_positions

if __name__ == "__main__":

    test = PiecePlacementAgent()
    tetris = Tetris(AgentGameConfig, AgentHandlingConfig)
    dropPos = list(test.get_drop_positions(tetris.currentTetromino, tetris).keys())[12]
    print(dropPos)
    for ac in Pathfinder.get_path(tetris, dropPos):
        print(actionObjToStr(ac))
    # print(test.get_drop_positions(tetris.currentTetromino, tetris))

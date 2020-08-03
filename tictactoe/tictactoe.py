"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_counter = 0
    o_counter = 0

    for row in board:
        for val in row:
            if val == "X":
                x_counter += 1
            if val == "O":
                o_counter += 1
    if x_counter == 0:
        return X
    elif x_counter > o_counter:
        return O
    elif x_counter == o_counter:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                moves.add((i, j))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] is not EMPTY:
        raise InvalidMove("Box is already filled!")
    else:
        new_board = deepcopy(board)
        new_board[i][j] = player(new_board)
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Row checking
    for row in board:
        if row.count(X) == 3:
            return X
        if row.count(O) == 3:
            return O

    # Column checking
    for col in range(len(board[0])):
        if board[0][col] == X and board[1][col] == X and board[2][col] == X:
            return X
        if board[0][col] == O and board[1][col] == O and board[2][col] == O:
            return O

    # Diagonal checking
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    if board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O

    # Anti-Diagonal checking
    if board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    if board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    else:
        empty_counter = 0
        for row in board:
            empty_counter += row.count(EMPTY)
        if empty_counter == 0:
            return True
        else:
            return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    verdict = winner(board)
    if verdict == X:
        return 1
    elif verdict == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
        
    if player(board) == O:
        move = min_value(board)[1]
    else:
        move = max_value(board)[1]
    return move

def max_value(board):
    if terminal(board):
        return [utility(board), None]
    v = float('-inf')
    best_move = None
    for action in actions(board):
        hypothetical_value = min_value(result(board, action))[0]
        if hypothetical_value > v:
            v = hypothetical_value
            best_move = action
    return [v, best_move]


def min_value(board):
    if terminal(board):
        return [utility(board), None]
    v = float('inf')
    best_move = None
    for action in actions(board):
        hypothetical_value = max_value(result(board, action))[0]
        if hypothetical_value < v:
            v = hypothetical_value
            best_move = action
    return [v, best_move]



class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidMove(Error):
    """Exception raised for invalid move.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

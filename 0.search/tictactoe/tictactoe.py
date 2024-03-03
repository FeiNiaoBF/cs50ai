"""
Tic Tac Toe Player
"""

import copy
import math

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
    nums_x, nums_o = 0, 0
    for row in board:
        for col in range(len(row)):
            if row[col] == X:
                nums_x += 1
            elif row[col] == O:
                nums_o += 1
    if nums_x == nums_o:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    ast = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                ast.append((i, j))
    return set(ast)




def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise ValueError("The action is empty")
    x, y = action[0], action[1]
    if board[x][y] == EMPTY:
        tmp = copy.deepcopy(board)  # 不能再原地修改
        tmp[x][y] = player(board)
        return tmp
    else:
        raise ValueError("Invalid block")



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # board not has all empty or board is ended in a tie
    # row win
    for r in range(len(board)):
        if board[r][0] == board[r][1] == board[r][2]:
            return board[r][0]
    # column win
    for c in range(len(board)):
        if board[0][c] == board[1][c] == board[2][c]:
            return board[0][c]
    # diagonally win
    if board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[1][1]
    elif board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[1][1]
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) in [X, O]:
        return True
    return EMPTY not in board[0] and EMPTY not in board[1] and EMPTY not in board[2]


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0




def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    p = player(board)
    actset = actions(board)
    val = []
    if p == X:
        for action in actset:
            val.append(minimax_O(result(board, action)))
        return list(actset)[max_X_index(val)]
    elif p == O:
        for action in actset:
            val.append(minimax_X(result(board, action)))
        return list(actset)[min_O_index(val)]


'''
1. 值的用处是分辨谁的步骤，如 val == 1， 则 X 在走
2. 最后要比较的是在 game over 时，minimax_X有1说明X可以赢，反之minimax_O有-1说明O可以赢
3. X & O 之间是“反抗的”，X 需要知道到达O的 Min valid 然后禁止O走，反之。

if:
1.                                      MAX: 1; p: X
2.                 MIN: -1; p: O              or           MIN: 0; p: O              or  ... (actions)
3.          MAX: 0; p: X or MAX: -1; p: X            MAX: 1; p: X or MAX: 0; p: X    or  ... (actions)
'''


def minimax_X(board):
    '''
    get max valid to X for actions
    '''
    if terminal(board):
        return utility(board)
    max_v = -16
    for action in actions(board):
        max_v = max(max_v, minimax_O(result(board, action)))
    return max_v

def minimax_O(board):
    '''
    get max valid to X for actions
    '''
    if terminal(board):
        return utility(board)
    min_v = 16
    for action in actions(board):
        min_v = min(min_v, minimax_X(result(board, action)))
    return min_v


def max_X_index(v):
    ix = 0
    maxV = v[0]
    for i,x in enumerate(v):
        if x > maxV:
            ix, maxV = i, x
    return ix

def min_O_index(v):
    ix = 0
    minV = v[0]
    for i,x in enumerate(v):
        if x < minV:
            ix, minV = i, x
    return ix



'''
Old func
'''
# def minimax_X(board, node):
#     node["player"] = X
#     valid = node["valid"] = utility(board)
#     # tmp_act = node["actions"]
#     for action in node["actions"]:
#         node["actions"] = actions(result(board, action))
#         min_O_node = minimax_O(result(board, action), node)
#         new_valid = min_O_node["valid"]
#         if max(new_valid, valid) != valid:         # O is minValid; X is maxValid
#             node["valid"] = new_valid
#             node["empty"] = min_O_node["empty"]
#             node["next"] = action
#         elif valid == new_valid and min_O_node["empty"] > node["empty"]:
#             node["valid"] = valid
#             node["empty"] = min_O_node["empty"]
#             node["next"] = action
#         if valid == 1 and nums_empty(board) == (node["empty"] + 1):
#             return node
#     return node

# def minimax_O(board, node):
#     node["player"] = O
#     valid = node["valid"] = utility(board)
#     # tmp_act = node["actions"]
#     for action in node["actions"]:
#         node["actions"] = actions(result(board, action))
#         max_X_node = minimax_X(result(board, action), node)
#         new_valid = max_X_node["valid"]
#         if max(new_valid, valid) != valid:         # O is minValid; X is maxValid
#             node["valid"] = new_valid
#             node["empty"] = max_X_node["empty"]
#             node["next"] = action
#         elif valid == new_valid and max_X_node["empty"] > node["empty"]:
#             node["valid"] = valid
#             node["empty"] = max_X_node["empty"]
#             node["next"] = action
#         if valid == -1 and nums_empty(board) == (node["empty"] + 1):
#             return node
#     return node



# # odd is X, even is O
# def nums_empty(board):
#     nums = 0
#     for i in range(len(board)):
#         for j in range(len(board[i])):
#             if board[i][j] == EMPTY:
#                 nums += 1
#     return nums

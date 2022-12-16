
# This is the base code for a greedy decision making algorithm for Reversi.
# It plays either on the corner or on the position that captures the maximum number of pieces.
# Adapted from: https://inventwithpython.com/chapter15.html

import random
from random import choice

from math import log,sqrt
from copy import deepcopy
from collections import Counter
import numpy as np
from reversi import getValidMoves
import reversi as rev
from time import perf_counter


def isOnCorner(board, x, y):
    lastX = len(board)-1
    lastY = len(board[0])-1
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or (x == lastX and y == 0) or (x == 0 and y == lastY) or (x == lastX and y == lastY)

def makeMove(board, tile, xstart, ystart):
    # Place the tile on the board at xstart, ystart, and flip any of the opponent's pieces.
    # Returns False if this is an invalid move, True if it is valid.
    tilesToFlip = rev.isValidMove(board, tile, xstart, ystart)
    # print()
    # for i in board:
    #     print(i)
    # print()
    # print(tile, xstart, ystart)
    if not tilesToFlip:
        raise ValueError('invalid play')
    board[xstart][ystart] = tile
    for x, y in tilesToFlip:
        board[x][y] = tile
    return board

def chooseGreedyMove(board, playerTile, epsilon=1.1, decrease=False):
    epsilon = epsilon**len(get_points(board)) if decrease else epsilon
    validMoves = rev.getValidMoves(board, playerTile)
    if not validMoves:
        return None  # passed

    # randomize the order of the possible moves
    random.shuffle(validMoves)

    if random.random() < epsilon:
        return choice(validMoves)

    # always go for a corner if available.
    for x, y in validMoves:
        if isOnCorner(board, x, y):
            return [x, y]

    # go through all the possible moves and remember the best scoring move
    bestScore = -1
    for x, y in validMoves:
        dupeBoard = rev.getBoardCopy(board)
        rev.makeMove(dupeBoard, playerTile, x, y)
        score = rev.getScoreOfBoard(dupeBoard)[playerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score

    return bestMove

def ucb(x,y,played_tiles,t):
    pass

def get_ucb(board,playerTile,played_tiles,t,valid_moves,ucb_val):
    valid_moves_points = []
    for x,y in valid_moves:
        copyb = deepcopy(board)
        copyb[x][y] = playerTile
        points = get_points(copyb)[playerTile]
        valid_moves_points.append(
            points + ucb_val*sqrt(log(t)/played_tiles[x][y])
        )
    return valid_moves_points

def selection(board,playerTile,played_tiles,t,valid_moves,ucb_val=1):
    valid_moves_points = get_ucb(board,playerTile,played_tiles,t,valid_moves,ucb_val)
    idx = valid_moves_points.index(max(valid_moves_points))
    return valid_moves[idx]

def expansion(board, playerTile,move):
    x,y = move
    board = makeMove(board,playerTile,x,y)
    return board

def get_points(board):
    return sum((Counter(i) for i in board),Counter())

def rollout(board,playerTile):
    EnemyTile = 'O' if playerTile == 'X' else 'X'
    pass_number = 0
    player_turn = True
    while pass_number <=1:
        actual_tile = playerTile if player_turn else EnemyTile
        vm = getValidMoves(board,actual_tile)
        if not vm:
            pass_number += 1
            player_turn = not player_turn
        else:
            pass_number = 0
            ephemeral_x,ephemeral_y = choice(vm)
            board = makeMove(board,actual_tile,ephemeral_x,ephemeral_y)
            player_turn = not player_turn
        # for i in board:
        #     print(i)
        # print()
    points = get_points(board)
    # print('\n\n')
    # for i in board:
    #     print(i)
    # print('\n')
    # print(points)
    if points[playerTile] > points[EnemyTile]:
        return 1
    if points[playerTile] == points[EnemyTile]:
        return 0
    return -1

def back_propagation(played_tiles,move):
    x,y = move
    played_tiles[x][y] += 1
    return played_tiles



def chooseMSCTMove(real_board, playerTile,played_tiles,t,lim_game=5,lim_rollout=0.5):
    possible = dict()
    game_timer = perf_counter()
    while (perf_counter() - game_timer) <= lim_game:
        board = deepcopy(real_board)
        validMoves = getValidMoves(board, playerTile)

        if not validMoves:
            return 'pass',played_tiles  # passed
        
        move = selection(board,playerTile,played_tiles,t,validMoves)

        board = expansion(board, playerTile,move)

        possible[tuple(move)] = 0

        rollou_timer = perf_counter()

        while (perf_counter() - rollou_timer) <= lim_rollout:
            possible[tuple(move)] += rollout(board,playerTile)

        played_tiles = back_propagation(played_tiles,move)
    print(possible)
    print('JOGADAS',t)
    for ii in played_tiles:
        print(ii)
    return sorted(possible.items(),key=lambda x:x[1],reverse=True)[0][0], played_tiles

    
    
    # randomize the order of the possible moves
    random.shuffle(validMoves)

    # always go for a corner if available.
    for x, y in validMoves:
        if isOnCorner(board, x, y):
            return [x, y]

    # go through all the possible moves and remember the best scoring move
    bestScore = -1
    for x, y in validMoves:
        dupeBoard = rev.getBoardCopy(board)
        rev.makeMove(dupeBoard, playerTile, x, y)
        score = rev.getScoreOfBoard(dupeBoard)[playerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score

    return bestMove

if __name__ == '__main__':
    b = rev.getNewBoard(stones=[(1,6), (6,6)])
    p = 'X'
    t = perf_counter()
    rollout(b,p)
    print(perf_counter() - t)
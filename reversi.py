########################
# Este arquivo tem a implementação das funções básicas para manipular o tabuleiro de Reversi,
# Baseado em código disponível em: https://inventwithpython.com/chapter15.html
########################


def drawBoard(board):
    # This function prints out the board that it was passed. Returns None.
    HLINE  = '   +' + ('---+' * len(board))
    #VLINE = '   |' + ('   |' * len(board))

    HEADINGS = '   '
    for x in range(len(board)):
        HEADINGS += f' {x:2d} ';

    print(HEADINGS)
    print(HLINE)

    for y in range(len(board[0])):
        #print(VLINE)
        print(f'{y:2d}', end=' ')
        for x in range(len(board)):
            print('| %s' % (board[x][y]), end=' ')
        print('|')
        #print(VLINE)
        print(HLINE)


def getNewBoard(sizeX=8, sizeY=8, stones=[]):
    assert (4 < sizeX < 100) and (4 < sizeY < 100) and (sizeX % 2) == 0 and (sizeY % 2) == 0
    # Creates a brand new, blank board data structure.
    board = []
    for i in range(sizeX):
        board.append([' '] * sizeY)

    # Blanks out the board it is passed, except for the original starting position.
    for x in range(len(board)):
        for y in range(len(board[0])):
            board[x][y] = ' '
    halfX = len(board) // 2
    halfY = len(board[0]) // 2
    
    # Starting pieces:
    board[halfX-1][halfY-1] = 'X'
    board[halfX-1][halfY]   = 'O'
    board[halfX]  [halfY-1] = 'O'
    board[halfX]  [halfY]   = 'X'
    
    # Stones (cannot play on them)
    for x,y in stones:
        board[x][y] = '*'
    
    return board


def isValidMove(board, tile, xstart, ystart):
    # Returns False if the player's move on space xstart, ystart is invalid.
    # If it is a valid move, returns a list of spaces that would become the player's if they made a move here.
    if not isOnBoard(board, xstart, ystart) or board[xstart][ystart] != ' ':
        return False
    board[xstart][ystart] = tile # temporarily set the tile on the board.

    if tile == 'X':
        otherTile = 'O'
    else:
        otherTile = 'X'

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection # first step in the direction
        y += ydirection # first step in the direction
        if isOnBoard(board, x, y) and board[x][y] == otherTile:
            # There is a piece belonging to the other player next to our piece.
            x += xdirection
            y += ydirection
            if not isOnBoard(board, x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(board, x, y): # break out of while loop, then continue in for loop
                    break
            if not isOnBoard(board, x, y):
                continue
            if board[x][y] == tile:
                # There are pieces to flip over. Go in the reverse direction until we reach the original space, noting all the tiles along the way.
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = ' ' # restore the empty space
    if len(tilesToFlip) == 0: # If no tiles were flipped, this is not a valid move.
        return False

    return tilesToFlip


def isOnBoard(board, x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x < len(board) and y >= 0 and y < len(board[0])


def getValidMoves(board, tile):
    # Returns a list of [x,y] lists of valid moves for the given player on the given board.
    validMoves = []
    for x in range(len(board)):
        for y in range(len(board[0])):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
    return validMoves


def getScoreOfBoard(board):
    # Determine the score by counting the tiles. Returns a dictionary with keys 'X' and 'O'.
    xscore = 0
    oscore = 0
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == 'X':
                xscore += 1
            if board[x][y] == 'O':
                oscore += 1
    return {'X':xscore, 'O':oscore}


def makeMove(board, tile, xstart, ystart):
    # Place the tile on the board at xstart, ystart, and flip any of the opponent's pieces.
    # Returns False if this is an invalid move, True if it is valid.
    tilesToFlip = isValidMove(board, tile, xstart, ystart)
    if tilesToFlip == False:
        return False
    board[xstart][ystart] = tile
    for x, y in tilesToFlip:
        board[x][y] = tile
    return True


def getBoardCopy(board):
    # Make a duplicate of the board list and return the duplicate.
    dupeBoard = getNewBoard(sizeX=len(board), sizeY=len(board[0]))
    for x in range(len(board)):
        for y in range(len(board[0])):
            dupeBoard[x][y] = board[x][y]
    return dupeBoard


def getBoardWithValidMoves(board, tile):
    # Returns a new board with . marking the valid moves the given player can make.
    dupeBoard = getBoardCopy(board)
    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = '.'
    return dupeBoard

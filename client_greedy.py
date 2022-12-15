import socket
import json
from copy import deepcopy

import reversi as rev
from greedy_base import chooseGreedyMove
from mcts import MonteCarloTreeSearchNode


def receiveMsg(conn):
    msg = conn.recv(256)
    if msg is not None:
        msg = msg.decode().strip()
    return msg


def sendMsg(conn, msg):
    conn.send(msg.encode())


def sendGreedyMove(client_socket, board, piece):
    # chooses first move
    move = chooseGreedyMove(board, piece)
    if move is None:
        moveMsg = 'pass'
    else:
        moveMsg = f"{move[0]} {move[1]}"
        rev.makeMove(board, piece, move[0], move[1])

    sendMsg(client_socket, moveMsg)
    print("My move:", moveMsg)

    # waits for confirmation
    assert receiveMsg(client_socket) == 'ok'


def sendMCTSMove(client_socket, moveMsg):
    sendMsg(client_socket, moveMsg if moveMsg == 'pass' else f"{moveMsg[0]} {moveMsg[1]}")
    print("My move:", moveMsg)

    # waits for confirmation
    assert receiveMsg(client_socket) == 'ok'


def message_to_board(full_message):
    str_board = full_message.split(maxsplit=1)
    assert str_board[0] == 'board', f'Received {full_message}'
    dict_board_params = json.loads(str_board[1])
    return rev.getNewBoard(**dict_board_params)


def client_program():
    host = socket.gethostname()  # assumes that server and clients are running on the same pc
    port = 5123  # socket server port number

    client_socket = socket.socket()
    client_socket.connect((host, port))

    data = receiveMsg(client_socket)
    assert data == 'name?'

    sendMsg(client_socket, 'greedy')

    data = receiveMsg(client_socket)

    while data != 'disconnect':
        print("NEW MATCH")

        # a new match is starting, so parse the board
        board = message_to_board(data)

        data = receiveMsg(client_socket)
        assert data.startswith('piece')

        if data == 'piece O':
            myPiece = 'O'
            advPiece = 'X'
            print('Playing with O')
        else:
            myPiece = 'X'
            advPiece = 'O'
            print('Playing with X (starting piece)')
            sendGreedyMove(client_socket, board, myPiece)

        # receives the adversary move
        data = receiveMsg(client_socket)

        while not data.startswith('end'):
            # parses adversary move
            advMove = data.strip().split()
            assert advMove[0] == advPiece, "Unexpected: " + str(advMove)

            if advMove[1] == 'pass':
                print("Adversary passed")
            else:
                print("Adversary move:", advMove[1], advMove[2])
                rev.makeMove(board, advPiece, int(advMove[1]), int(advMove[2]))

            # computes and sends a greedy move
            sendGreedyMove(client_socket, board, myPiece)

            # waits for adversary move
            data = receiveMsg(client_socket)

        print("Final score:", data[data.find(' ') + 1:])
        data = receiveMsg(client_socket)

    print("All matches finished by the server.")
    client_socket.close()  # close the connection


def client_program_mcts():
    host = socket.gethostname()  # assumes that server and clients are running on the same pc
    port = 5123  # socket server port number

    client_socket = socket.socket()
    client_socket.connect((host, port))

    data = receiveMsg(client_socket)
    assert data == 'name?'

    sendMsg(client_socket, 'mcts')

    data = receiveMsg(client_socket)

    while data != 'disconnect':
        print("NEW MATCH")

        # a new match is starting, so parse the board
        board = message_to_board(data)

        data = receiveMsg(client_socket)
        assert data.startswith('piece')

        if data == 'piece O':
            myPiece = 'O'
            advPiece = 'X'
            print('Playing with O')
            root = MonteCarloTreeSearchNode(deepcopy(board), False, None, None, myPiece)
        else:
            myPiece = 'X'
            advPiece = 'O'
            print('Playing with X (starting piece)')
            root = MonteCarloTreeSearchNode(deepcopy(board), True, None, None, myPiece)
            root = root.best_action()
            move = root.parent_action
            if root != 'pass':
                move = root.parent_action
                # root.update_passes(0)
            else:
                # passCount += 1
                move = root
            sendMCTSMove(client_socket, move)

        # receives the adversary move
        data = receiveMsg(client_socket)
        print(data)

        while not data.startswith('end'):
            # parses adversary move
            advMove = data.strip().split()
            print(advMove)
            assert advMove[0] == advPiece, "Unexpected: " + str(advMove)

            if advMove[1] == 'pass':
                print("Adversary passed")
                root = MonteCarloTreeSearchNode(root.state, True, root, root.parent_action, root.tile)
            else:
                print("Adversary move:", advMove[1], advMove[2])
                print('before')
                rev.drawBoard(board)
                print('after')
                rev.makeMove(board, advPiece, int(advMove[1]), int(advMove[2]))
                rev.drawBoard(board)

                print('root before')
                rev.drawBoard(root.state)

                root = MonteCarloTreeSearchNode(deepcopy(board), True, root, root.parent_action, root.tile)
                print('root after')
                rev.drawBoard(root.state)
            # print('BOARD INTERNO')
            # rev.drawBoard(board)

            # computes and sends a greedy move
            # sendGreedyMove(client_socket, board, myPiece)
            root = root.best_action()
            move = root.parent_action
            if root != 'pass':
                move = root.parent_action
                # root.update_passes(0)
            else:
                # passCount += 1
                move = root
            sendMCTSMove(client_socket, move)
            # waits for adversary move
            data = receiveMsg(client_socket)

        print("Final score:", data[data.find(' ') + 1:])
        data = receiveMsg(client_socket)

    print("All matches finished by the server.")
    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program_mcts()

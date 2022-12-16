import socket
import time
import json

import reversi as rev


class Player:
    def __init__(self, name, conn, piece):
        self.name = name
        self.conn = conn
        self.piece = piece
        self.penalty = 0


def server_program():
    host = socket.gethostname()
    port = 5123  # initiate port number above 1024

    server_socket = socket.socket()  # get instance

    server_socket.bind((host, port))

    print("STARTING REVERSI SERVER")
    print("- waiting for two players (clients)")

    # servidor ouve dois clientes por vez - um por player
    server_socket.listen(2)

    # aceita a conexão com o 1o cliente
    conn1, address1 = server_socket.accept()  # accept new connection
    print(" - player 1 connected from: " + str(address1))
    conn1.send("name?".encode())
    p1name = conn1.recv(128).decode()
    print(" - player 1 is ", p1name)

    player1 = Player(p1name, conn1, '-')

    # aceita a conexão com o 2o cliente
    conn2, address2 = server_socket.accept()  # accept new connection
    print(" - player 2 connected from: " + str(address2))
    conn2.send("name?".encode())
    p2name = conn2.recv(128).decode()
    if p2name == p1name:
        p2name = p2name + '_'
    print(" - player 2 is ", p2name)

    player2 = Player(p2name, conn2, '-')

    # inicia as partidas
    overall_results = {p1name: 0, p2name: 0}

    print("MATCH 1")
    board_param = dict(sizeX=8, sizeY=8, stones=[(1, 6), (6, 6)])
    serve_match(player1, player2, board_param, overall_results)

    print("MATCH 2")
    serve_match(player2, player1, board_param, overall_results)

    print("MATCH 3")
    serve_match(player1, player2, board_param, overall_results)

    print("MATCH 4")
    serve_match(player2, player1, board_param, overall_results)

    print("MATCH 5")
    serve_match(player1, player2, board_param, overall_results)

    print("MATCH 6")
    serve_match(player2, player1, board_param, overall_results)

    print("ALL MATCHES ENDED")

    print(" -- FINAL RESULT ---")
    print("|  Player %s: %s points" % (player1.name, overall_results[player1.name]))
    print("|  Player %s: %s points" % (player2.name, overall_results[player2.name]))
    print(" -------------------")

    sendMsg(player1, "disconnect")
    sendMsg(player2, "disconnect")
    time.sleep(1)

    player1.conn.close()
    player2.conn.close()
    server_socket.close()


def board_to_message(dict_board_params):
    return "board " + json.dumps(dict_board_params)


def sendMsg(player, msg):
    player.conn.send(msg.encode())


def receiveMsg(player):
    return player.conn.recv(128).decode().strip()


def receiveValidMoveMsg(player, board):
    start_time = time.time() - 0.1  # to give +0.1s due to loss of time in overhead
    for trials in range(2):
        moveMsg = receiveMsg(player)
        if moveMsg == 'pass':
            player.penalty += int((time.time() - start_time) / 3)
            print('Penalty:', player.penalty)
            return moveMsg

        wellFormattedMsg = True
        moveMsg = moveMsg.split()

        if len(moveMsg) != 2:
            wellFormattedMsg = False
        else:
            try:
                moveX = int(moveMsg[0])
                moveY = int(moveMsg[1])
                wellFormattedMsg = True
            except Exception as exc:
                wellFormattedMsg = False

        if wellFormattedMsg and rev.isValidMove(board, player.piece, moveX, moveY):
            player.penalty += int((time.time() - start_time) / 3)
            print('Penalty:', player.penalty)
            return (moveX, moveY)
        else:
            sendMsg(player, "invalid")

    return 'abort'


def serve_match(playerX, playerO, dict_board_params, overall_results):
    showHints = True
    board = rev.getNewBoard(**dict_board_params)

    # envia tabuleiro e peças de cada player
    sendMsg(playerX, board_to_message(dict_board_params))
    sendMsg(playerO, board_to_message(dict_board_params))

    sendMsg(playerX, "piece X")
    playerX.piece = 'X'
    playerX.penalty = 0

    sendMsg(playerO, "piece O")
    playerO.piece = 'O'
    playerO.penalty = 0

    player, advPlayer = playerX, playerO
    passCount = 0

    while passCount < 2:
        if showHints:
            validMovesBoard = rev.getBoardWithValidMoves(board, player.piece)
            rev.drawBoard(validMovesBoard)
        else:
            rev.drawBoard(board)

        printScore(playerX, playerO, board)
        print("Player %s's turn" % player.name)
        move = receiveValidMoveMsg(player, board)

        if move == 'abort':
            sendMsg(player, "ok")  # para liberar o client do seu loop de ação
            print(f"Match aborted because {player.name} sent too many invalid moves.")
            player.penalty = 100
            break

        if move == 'pass':
            passCount += 1
            sendMsg(player, "ok")
            if passCount < 2:
                sendMsg(advPlayer, f"{player.piece} pass")
            print(f"{player.name} passed")

            player, advPlayer = advPlayer, player

        else:
            passCount = 0
            rev.makeMove(board, player.piece, move[0], move[1])

            sendMsg(player, "ok")
            sendMsg(advPlayer, f"{player.piece} {move[0]} {move[1]}")
            print(f"{player.name} move:", move[0], move[1])

            player, advPlayer = advPlayer, player

    # print("Two consecutive passes.")
    print("End of game.")

    # mostra e envia os scores finais
    rev.drawBoard(board)
    scores = printScore(playerX, playerO, board)
    scores['X'] = scores['X'] - playerX.penalty
    scores['O'] = scores['O'] - playerO.penalty

    scoreMsg = f"end X {scores['X']} O {scores['O']}"
    sendMsg(playerX, scoreMsg)
    sendMsg(playerO, scoreMsg)
    if scores['X'] > scores['O']:
        overall_results[playerX.name] += 1.0
    elif scores['O'] > scores['X']:
        overall_results[playerO.name] += 1.0
    else:
        overall_results[playerX.name] += 0.5
        overall_results[playerO.name] += 0.5
    # print(overall_results)

def printScore(playerX, playerO, board):
    scores = rev.getScoreOfBoard(board)
    print(" -- SCORE ---------")
    print("|  Player %s (X): %s (-%s) points" % (playerX.name, scores['X'], playerX.penalty))
    print("|  Player %s (O): %s (-%s) points" % (playerO.name, scores['O'], playerO.penalty))
    print(" ------------------")
    return scores


if __name__ == '__main__':
    server_program()

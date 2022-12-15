import socket
import time
import json

import reversi as rev


class Player:
    def __init__(self, name, conn, piece):
        self.name = name
        self.conn = conn
        self.piece = piece


def server_program():
    host = socket.gethostname()
    port = 5123  # initiate port number above 1024

    server_socket = socket.socket()  # get instance
   
    server_socket.bind((host, port))

    print("STARTING REVERSI SERVER")
    print("- waiting for two players (clients)")

    # servidor ouve dois clientes por vez - um por player
    server_socket.listen(2)

    conn1, address1 = server_socket.accept()  # accept new connection
    print(" - player 1 connected from: " + str(address1))
    conn1.send("name?".encode())
    p1name = conn1.recv(128).decode()
    print(" - player 1 is ", p1name)
    
    player1 = Player(p1name, conn1, '-')

    conn2, address2 = server_socket.accept()  # accept new connection
    print(" - player 2 connected from: " + str(address2))
    conn2.send("name?".encode())
    p2name = conn2.recv(128).decode()
    print(" - player 2 is ", p2name)
    
    player2 = Player(p2name, conn2, '-')

    # inicia as partidas
    print("MATCH 1")
    board_param = dict(sizeX=8, sizeY=8, stones=[(1,6), (6,6)])
    serve_match(player1, player2, board_param)
    
    print("MATCH 2")
    serve_match(player2, player1, board_param)

    print("ALL MATCHES ENDED")

    sendMsg(player1, "disconnect")
    sendMsg(player2, "disconnect")
    time.sleep(1)

    player1.conn.close()
    player2.conn.close()


def board_to_message(dict_board_params):
    return "board " + json.dumps(dict_board_params)


def sendMsg(player, msg):
    player.conn.send(msg.encode())


def receiveMsg(player):
    return player.conn.recv(128).decode().strip()


def serve_match(playerX, playerO, dict_board_params):
    showHints = True
    mainBoard = rev.getNewBoard(**dict_board_params)

    # envia tabuleiro e peças de cada player
    sendMsg(playerX, board_to_message(dict_board_params))
    sendMsg(playerO, board_to_message(dict_board_params))
 
    sendMsg(playerX, "piece X")
    playerX.piece = 'X'
    
    sendMsg(playerO, "piece O")
    playerO.piece = 'O'
    
    player, advPlayer = playerX, playerO
    moveX, moveY = -1, -1
    passCount = 0

    while passCount < 2:
        if showHints:
            validMovesBoard = rev.getBoardWithValidMoves(mainBoard, player.piece)
            rev.drawBoard(validMovesBoard)
        else:
            rev.drawBoard(mainBoard)

        printScore(playerX, playerO, mainBoard)
        
        moveMsg = receiveMsg(player)
        
        if moveMsg == 'pass':
            passCount += 1
            sendMsg(player, "ok")
            if passCount < 2:
                sendMsg(advPlayer, f"{player.piece} pass")
            print(f"{player.name} passed")

            player, advPlayer = advPlayer, player

        else:
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

            if wellFormattedMsg and rev.isValidMove(mainBoard, player.piece, moveX, moveY):
                passCount = 0
                rev.makeMove(mainBoard, player.piece, moveX, moveY)
                
                sendMsg(player, "ok")
                sendMsg(advPlayer, f"{player.piece} {moveX} {moveY}")
                print(f"{player.name} move:", moveX, moveY)

                player, advPlayer = advPlayer, player
            else:
                sendMsg(player, "invalid")
                continue

    print("Two consecutive passes.")
    print("End of game.")

    # mostra e envia os scores finais
    rev.drawBoard(mainBoard)
    scores = printScore(playerX, playerO, mainBoard)
    
    scoreMsg = f"end X {scores['X']} O {scores['O']}"
    sendMsg(playerX, scoreMsg)
    sendMsg(playerO, scoreMsg)


def printScore(playerX, playerO, board):
    scores = rev.getScoreOfBoard(board)
    print(" -- SCORE ---------")
    print("|  Player %s (X): %s points" % (playerX.name, scores['X']))
    print("|  Player %s (O): %s points" % (playerO.name, scores['O']))
    print(" ------------------")
    return scores


if __name__ == '__main__':
    server_program()

import socket


def receiveMsg(conn):
    msg = conn.recv(256)
    if msg is not None:
        msg = msg.decode().strip()
    return msg


def sendMsg(conn, msg):
    conn.send(msg.encode())


def sendHumanMove(client_socket):
    # repeats until a correctly formatted message is given
    while True:
        moveMsg = input("Your move? -> ").lower().strip()
        if len(moveMsg) == 0:
            continue
        # sends and waits for confirmation
        sendMsg(client_socket, moveMsg)
        data = receiveMsg(client_socket)
        if data == 'ok':
            break
        else:
            print('Server returned:', data)
            print('Type either "pass" or type two integer representing board positions.')


def client_program():
    host = socket.gethostname()  # assumes that server and clients are running on the same pc
    port = 5123                  # socket server port number

    client_socket = socket.socket()
    client_socket.connect((host, port))

    data = receiveMsg(client_socket)
    assert data == 'name?'

    msg = input("Your name? -> ").lower().strip()
    sendMsg(client_socket, msg)
    
    data = receiveMsg(client_socket)

    while data != 'disconnect':
        print("NEW MATCH")

        # receive board parameters
        assert data.startswith('board') # in this version, we don't parse the board
        print("Board parameters:", data.split(maxsplit=1)[1])

        data = receiveMsg(client_socket)
        assert data.startswith('piece')

        if data == 'piece O':
            myPiece  = 'O'
            advPiece = 'X'
            print('Playing with O')
        else:
            myPiece = 'X'
            advPiece = 'O'
            print('Playing with X (starting piece)')
            sendHumanMove(client_socket)

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

            # reads a move from the default input, then sends it
            sendHumanMove(client_socket)

            # waits for adversary move
            data = receiveMsg(client_socket)
        
        print("Final score:", data[data.find(' ')+1:])
        data = receiveMsg(client_socket)

    print("All matches finished by the server.")
    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()

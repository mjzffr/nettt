#!/usr/bin/env python2
import socket
import ttt

HOST = 'localhost'
PORT = 50000

class Server:
    # manages muiltiple games
    # asks right client for their move
    # notifies other client of their opponent's move
    # notifies both clients of game result
    # pairs clients up into games

    def __init__(self):
        pass

    def start_server(self):

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((HOST, PORT))
        serversocket.listen(5)

        (clientsocket, address) = serversocket.accept()
        print 'Connection from' + str(address)
        clientsocket.send('Hello!\n')
        while True:
            msg = clientsocket.recv(8)
            #print(msg)
            if msg.startswith('exit'):
                print "no!"
                break
            else:
                print msg
        clientsocket.close()
        exit()

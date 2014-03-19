#!/usr/bin/env python2
import socket
import ttt
import logging
import sys
import select

HOST = 'localhost'
PORT = 50000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('server.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ' +
                              '%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Session:
    ''' Keeps track of game and its two participating clients.'''
    def __init__(self, firstclient):
        self.player1 = firstclient
        self.player2 = None
        self.game = ttt.TicTacToeGame()
        # queue of messages?


class Server:
    def __init__(self):
        self.readables = []
        self.writables = []
        self.allsockets = []
        # all initiated games
        self.sessions = []
        # which clients belong to which games
        self.sessiondict = {}


    def run(self):
        listenersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #prevent the "already in use error"
        listenersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # TODO: bind raises an exception if port is already in use
        listenersock.bind((HOST, PORT))
        listenersock.listen(5)
        print "Server on"

        self.readables = [listenersock, sys.stdin]
        self.allsockets = [listenersock]

        while True:
            # wait for at least one of the sockets to be ready
            (ready_rds, ready_wrs,
                exceptional) = select.select(self.readables, self.writables,
                                             self.allsockets, 60)

            # Process incoming data
            for r in ready_rds:
                # accept a client connection
                if r is listenersock:
                    clientsock, clientaddr = listenersock.accept()
                    for iolist in [self.readables, self.writables,
                                   self.allsockets]:
                        iolist.append(clientsock)
                    # assuming that the accept() call was successful
                    clientsock.send("Hello to " + str(clientaddr) + '\n')
                    # TODO if there are any unpaired sessions, add the client to one
                    # TODO how to keep track of which client is in which session?
                    # otherwise create a new lonely session for this client
                    # assumption: a client can be in only one session
                    #gamesession = Session(clientsock)
                    #self.sessiondict[clientsock] = gamesession
                    #self.sessions.append(Session(clientsock))
                elif r is sys.stdin:
                    if (sys.stdin.readline()).strip() == 'exit':
                        # (?): assume that client is responsible for closing
                        # its connection
                        self.listenersock.close()
                        print "Server off"
                        quit()
                # collect a message from each ready client
                else:
                    pass
                    #self.broadcast_msg(r, ready_wrs)

            # disconnect from any other errorful clients
            # (One "normally" leaves the error list in select empty
            # according to http://docs.python.org/3/howto/sockets.html)
            for s in exceptional:
                for iolist in [self.readables, self.writables,
                               self.allsockets]:
                    if s in iolist:
                        iolist.remove(s)
                s.close()

    def broadcast_msg(self, source, destinations):
        ''' Send message from source to all other clients in destinations list.
        `destinations` is the result of a select call: if a client wasn't ready
        at that moment, it will never receive this message!
        '''
        msg = source.recv(SIZE)
        if msg:
            for recipient in destinations:
                if recipient is not source:
                    try:
                        recipient.send(msg)
                    except socket.error as e:
                        # remote peer disconnected
                        if isinstance(e.args, tuple) and e[0] == errno.EPIPE:
                            self.disconnect_client(recipient)
                        else:
                            # some other unanticipated issue. :(
                            raise e
        else:
            # no data received means that source has disconnected
            self.disconnect_client(source)

    def disconnect_client(self, s):
        print "Disconnecting: " + str(s.getpeername())
        if s in self.writables:
            self.writables.remove(s)
        if s in self.readables:
            self.readables.remove(s)
        if s in self.allsockets:
            self.allsockets.remove(s)
        s.close()

if __name__ == "__main__":
    Server().run()

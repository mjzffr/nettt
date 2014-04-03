#!/usr/bin/env python2
import socket
import ttt
import logging
import sys
import select
import time

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

    # For now, if a player leaves a gamesession, that gamesession is
    # concluded
    # and his partner is automatically put in a new empty gamesession.

class Server:
    def __init__(self):
        self.readables = []
        self.writables = []
        self.allsockets = []
        # all initiated games
        self.sessions = []
        # which clients belong to which games
        self.sessiondict = {}
        # a queue of messages?
        # dictionary of sock : reuqests, dictionary  sock: responses?

    def run(self):
        listenersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #prevent the "already in use error"
        listenersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listenersock.setblocking(False)
        # TODO: bind raises an exception if port is already in use
        listenersock.bind((HOST, PORT))
        listenersock.listen(5)
        print "Server on"

        self.readables = [listenersock, sys.stdin]
        self.allsockets = [listenersock]

        while True:
            # wait for at least one of the sockets to be ready
            (ready_rds, ready_wrs,
                exceptional) = select.select(self.readables,
                                             self.writables,
                                             self.allsockets, 60)

            # Process incoming data
            for r in ready_rds:
                # accept a client connection
                if r is listenersock:
                    clientsock, clientaddr = listenersock.accept()
                    clientsock.setblocking(False)
                    for iolist in [self.readables, self.writables,
                                   self.allsockets]:
                        iolist.append(clientsock)
                    print 'Connected to ' + str(clientaddr)
                    #logger.info('Connected to ' + str(clientaddr))
                    #self.assign_to_session(clientsock)
                elif r is sys.stdin:
                    if (sys.stdin.readline()).strip() == 'exit':
                        listenersock.close()
                        print "Server off"
                        sys.exit()
                # collect a message from each ready client
                else:
                    print 'client recv'
                    print (ready_rds, ready_wrs, exceptional)
                    # TODO
                    # results in err104 connection reset by peer if client
                    # has crashed
                    # When client closes socket, empty string is received
                    message = r.recv(8)
                    if not message:
                        self.delete_socket(r)
                    #else: # TEMP, TODO
                        # _, ready_to_write, _ = select.select([],[r],[],1)
                        # if ready_to_write:
                        #     ready_to_write[0].send('hello')
                        #     ready_to_write[0].send('hello')

            # for w in ready_wrs:
            #     print 'client send'
            #     print (ready_rds, ready_wrs, exceptional)
            # TODO when sending: recover from err 32 broken pipe in case
            # client quits
            #     w.send('hello')

            for e in exceptional:
                self.delete_socket(e)

    def delete_socket(self, sock):
        for iolist in [self.readables, self.writables, self.allsockets]:
            if sock in iolist:
                iolist.remove(sock)
        sock.close()
        print 'closed socket'
                #logger.info('Closed a socket.')

    # @property
    # def num_sessions(self):
    #     return len(set(self.sessiondict.values()))




    def assign_to_session(client):
        if len(self.sessions) != 0 and not self.sessions[-1].player2:
            # add client to last-created session; it is unpaired
            self.sessiondict[clientsock] = self.sessions[-1]
            self.sessions[-1].player2 = clientsock
            # send message to client that it is p1 and it's p2's turn
        else:
            gamesession = Session(clientsock)
            # TODO send message to client that it is p1 and it's p1's turn
            self.sessiondict[clientsock] = gamesession
            self.sessions.append(gamesession)


    # def broadcast_msg(self, source, destinations):
    #     ''' Send message from source to all other clients in destinations list.
    #     `destinations` is the result of a select call: if a client wasn't ready
    #     at that moment, it will never receive this message!
    #     '''
    #     msg = source.recv(SIZE)
    #     if msg:
    #         for recipient in destinations:
    #             if recipient is not source:
    #                 try:
    #                     recipient.send(msg)
    #                 except socket.error as e:
    #                     # remote peer disconnected
    #                     if isinstance(e.args, tuple) and e[0] == errno.EPIPE:
    #                         self.disconnect_client(recipient)
    #                     else:
    #                         # some other unanticipated issue. :(
    #                         raise e
    #     else:
    #         # no data received means that source has disconnected
    #         self.disconnect_client(source)

    def disconnect_client(self, s):
        # TODO discard session that the client belonged to
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

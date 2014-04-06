#!/usr/bin/env python2
import socket
import ttt
import logging
import sys
import select
import random


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('server.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ' +
                              '%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Session(object):
    ''' Keeps track of game and its two participating client sockets.'''
    def __init__(self, firstclient, sessiontype):
        self.players = {ttt.BSTATES['P1']:firstclient}
        self.game = ttt.TicTacToeGame(start=random.choice([ttt.BSTATES['P1'],
                                                           ttt.BSTATES['P2']]))
        # 'a' for ai, 'p' for person
        self.sessiontype = sessiontype
        if sessiontype == 'a':
            self.players[ttt.BSTATES['P2']] = 'computer'


    def add_player(self, player2):
        ''' returns True if there was room for a second player (adding
            a second player succeeded)
        '''
        if self.players.get(ttt.BSTATES['P2']):
            return False
        else:
            self.players[ttt.BSTATES['P2']] = player2

        return True

    # For now, if a player leaves a gamesession, that gamesession is
    # concluded
    # and his partner is automatically put in a new empty gamesession.

class Server(object):
    HOST = 'localhost'
    PORT = 50000

    def __init__(self):
        self.readables = []
        self.writables = []
        self.allsockets = []
        # which clients belong to which games (sock:session)
        self.sessiondict = {}
        # sock:queue (queue of requests to respond to)
        self.requests = {}

        self.listenersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #prevent the "already in use error"
        self.listenersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenersock.setblocking(False)
        # TODO: bind raises an exception if port is already in use
        self.listenersock.bind((self.HOST, self.PORT))
        self.listenersock.listen(5)
        print "Server on"


    def run(self):
        self.readables = [self.listenersock, sys.stdin]
        self.allsockets = [self.listenersock]
        while True:
            # wait for at least one of the sockets to be ready
            (ready_rds, ready_wrs,
                exceptional) = select.select(self.readables,
                                             self.writables,
                                             self.allsockets, 60)
            self.process_requests(ready_rds)
            self.process_responses(ready_wrs)
            for e in exceptional:
                self.delete_socket(e)

    def process_requests(self, ready_rds):
        for r in ready_rds:
                if r is self.listenersock:
                    clientsock, clientaddr = self.listenersock.accept()
                    clientsock.setblocking(False)
                    for iolist in [self.readables, self.writables,
                                   self.allsockets]:
                        iolist.append(clientsock)
                    # initialize request queue
                    self.requests[clientsock] = []
                    print 'Connected to ' + str(clientaddr)
                    #logger.info('Connected to ' + str(clientaddr))
                elif r is sys.stdin:
                    if (sys.stdin.readline()).strip() == 'exit':
                        self.listenersock.close()
                        print "Server off"
                        sys.exit()
                # collect a message from each ready client
                else:
                    # TODO
                    # results in err104 connection reset by peer if client
                    # has crashed
                    # When client closes socket, empty string is received
                    message = r.recv(1024)
                    if not message:
                        self.disconnect_client(r)
                    else:
                        self.requests[r].append(message)
                        print message

    def process_responses(self, ready_wrs):
        # clients who are ready for sending and have sent in a request
        waiting_clients = set(ready_wrs).intersection({i for i in
                                              set(self.requests.keys())
                                              if self.requests[i]})
        for w in waiting_clients:
            print 'client send'
            # TODO when sending: recover from err 32 broken pipe in case
            # client quits
            result = w.sendall('+1,-1')
            if result is None:
                #success
                del self.requests[w][0]
                print len(self.requests[w])

        pass

    def disconnect_client(self, sock):
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

if __name__ == "__main__":
    Server().run()

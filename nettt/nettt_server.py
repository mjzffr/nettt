#!/usr/bin/env python2
import socket
import ttt
import logging
import sys
import select
import random
import pdb


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
        self.game = ttt.TicTacToeGame(first=random.choice([ttt.BSTATES['P1'],
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
    # end of message marker
    EOM = '\n'

    def __init__(self):
        self.readables = []
        self.writables = []
        self.allsockets = []
        # which clients belong to which games (sock:session)
        self.sessiondict = {}
        # sock:queue (queue of responses to send)
        self.responses = {}

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
            for sock in exceptional:
                self.delete_socket(sock)

    def process_requests(self, ready_rds):
        def recv_all(sock):
            message = ''
            while not message.endswith(self.EOM):
                # TODO: results in err104 connection reset by peer if client
                # has crashed
                piece = sock.recv(1024)
                if not piece:
                    self.disconnect_client(sock)
                    return ''
                else:
                    message = ''.join([message, piece])
            return message.rstrip()

        for reader in ready_rds:
                if reader is self.listenersock:
                    clientsock, clientaddr = self.listenersock.accept()
                    clientsock.setblocking(False)
                    for iolist in [self.readables, self.writables,
                                   self.allsockets]:
                        iolist.append(clientsock)
                    # initialize response queue
                    self.responses[clientsock] = []
                    print 'Connected to ' + str(clientaddr)
                    #logger.info('Connected to ' + str(clientaddr))
                elif reader is sys.stdin:
                    if (sys.stdin.readline()).strip() == 'exit':
                        self.shutdown()
                # collect a message from each ready client
                else:
                    request = recv_all(reader)
                    print request #XXX
                    if request:
                        self.queue_response(request, reader)

    def shutdown(self):
        for sock in self.allsockets:
            sock.close()
        print 'Server off'
        sys.exit()

    def process_responses(self, ready_wrs):
        # clients who are ready for sending and for which there is a response
        waiting_clients = set(ready_wrs).intersection({i for i in
                                              set(self.responses.keys())
                                              if self.responses[i]})
        for w in waiting_clients:
            # TODO when sending: recover from err 32 broken pipe in case
            # client quits
            try:
                w.sendall(''.join([self.responses[w][0],self.EOM]))
                # remove request from queue upon successful response
                del self.responses[w][0]
            except socket.error as e:
                logger.info('Failed to send message: %s' % e)

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

    @property
    def sessions(self):
        return set(self.sessionsdict.values())

    def find_free_session(self):
        ''' returns Session that does not have two players yet or
        None if such a session doesn't exist
        '''
        for session in self.sessions:
            if not session.players.get(ttt.BSTATES['P2']):
                return session

    def assign_to_session(self, client, sessiontype):
        ''' Adds client to an existing or new Session, updates sessiondict and
            queues reponses to session clients if their Session is ready.
            returns the resulting Session
        '''
        def msg(player, session):
            p1 = ttt.BSTATES['P1']
            p2 = ttt.BSTATES['P2']
            pid = p1 if player is session.players[p1] else p2
            turn = session.game.current_player
            return ','.join([str(pid), str(turn)])

        # check if client already in session
        existingsession = self.sessiondict.get(client)
        if existingsession:
            return existingsession

        if sessiontype == 'p':
            free_session = self.find_free_session()
            if free_session:
                free_session.add_player(client)
                self.sessiondict[client] = free_session
                # add response for both session players to response queue
                self.responses[client].append(msg(client, free_session))
                partner = free_session.players[ttt.BSTATES['P1']]
                self.responses[partner].append(msg(partner, free_session))
                return free_session

        gamesession = Session(client, sessiontype)
        self.sessiondict[client] = gamesession
        # TODO: if playing against ai, queue response to player right away
        if sessiontype == 'a':
            self.responses[client].append(msg(client,gamesession))
            print self.responses[client] # XXX
        return gamesession

    def queue_response(self, request, clientsock):
        if request in ['a','p']:
            self.assign_to_session(clientsock, request)


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

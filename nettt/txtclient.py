import ttt
import socket
import errno
import sys
import logging
import select
import pdb

# general log setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('client.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ' +
                              '%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TTTClient(object):
    # end-of-message marker
    EOM = '\n'
    HOST = 'localhost'
    PORT = 50000
    SIZE = 3

    def __init__(self):
        self.sock = None
        self.sessiontype = 'a'
        self.reset_connection()
        self.lastboardstr = ''


    def reset_connection(self):
        ''' Called in __init__ and when peer disconnects. '''
        self.disconnect()
        self.sock = socket.socket()
        self.connected = False
        self.starter = None
        # (p)erson or (a)i
        self.role = None

    @property
    def i_go_first(self):
        return self.starter == self.role

    def connect(self):
        if self.connected:
            return
        def raise_surprise(e, errcodes):
            ''' Propagates exception e if it doesn't match any expected
                errcodes '''
            if isinstance(e.args,tuple) and any([e[0] == c for c in errcodes]):
                # we were expecting this one
                logger.info(str(e))
            else:
                # surprise!
                raise e
        try:
            self.sock.connect((self.HOST, self.PORT))
            self.connected = True
            # Only the connection phase is blocking!
            self.sock.setblocking(False)
        except socket.gaierror as e:
            #TODO improve logging clarity
            logger.info('Socket gaierror' + str(e))
        except socket.error as e:
            if isinstance(e.args, tuple) and e[0] == errno.EISCONN:
               logger.info('Already connected')
               self.connected = True
            raise_surprise(e,[errno.ECONNABORTED, errno.ECONNREFUSED])

    def request_session(self):
        ''' Asks server for a game and a partner by sending the session
            type
        '''
        logger.info('Requested session type' + self.sessiontype)
        self.sock.sendall(''.join([self.sessiontype, self.EOM]))

    def recv_all(self):
        ''' recvs data until end-of-message marker is encountered
        It is possible that two messages will be sent in one shot.
        The only time two messages should be received if it's the initial
        server response OR the game is over.
        '''
        message = ''
        while not message.endswith(self.EOM):
            if len(message) > 100:
                errmsg = 'Length limit exceeded'
                logger.info(errmsg)
                raise Exception(errmsg)
            piece = self.sock.recv(64)
            if not piece:
                message = ''
                break
            else:
                message = ''.join([message, piece])
        allmessages = message.rstrip().split('\n')
        logger.info('Response: ' + str(allmessages))
        if not allmessages or not allmessages[0]:
            logger.info('Server disconnected?')
            raise Exception('Server disconnected?')
        return allmessages

    def validate_response(self, allmessages):
        if 'error' in allmessages:
            raise Exception('Rejected by server')
        if 'gg' in allmessages: #xxx
            print "GAME OVER" # xxx
        if len(allmessages) > 2:
            raise Exception('Protocol violated')
        if len(allmessages) == 2:
            if not self.valid_boardstr(allmessages[1]):
                raise Exception('Protocol violated')

    def update_board_get_alert(self):
        ''' Updates board to string last received from server. Returns
        additional info (alert) sent by server, if any. "role" and "gg" are
        examples of alerts. What message list might look like:
        - [role]            <-- beginning of p game, or ai game (ai plays 2nd)
        - [role, boardstr]  <-- beginning of ai game, ai plays first
        - [boardstr]        <-- mid-game
        - [gg, boardstr]    <-- after final move of game
        - [...,error,...]   <-- server did not like what client sent
        '''
        messages = self.recv_all()
        self.validate_response(messages)
        if len(messages) == 2:
            self.lastboardstr = messages[1]
        elif self.valid_boardstr(messages[0]):
            self.lastboardstr = messages[0]
            return
        return messages[0]

    def await_partner(self):
        ''' Updates role and starter. Expects to recv string of the form
        'x,y' where x and y must be 1 or -1, x represents client's role and
        y represents who gets the first move.
        '''
        response = self.update_board_get_alert()
        print response # XXX
        self.role, self.starter = [int(i) for i in response.split(',', 1)]
        if self.role not in [1, -1] or self.starter not in [1, -1]:
            logger.info(errmsg)
            raise Exception('Protocol violated')

    def await_gameupdate(self):
        ''' Returns new board/game state recv'd from server.'''
        response = self.update_board_get_alert()
        if response:
            print "Yep, game over. Now what?"

    def valid_boardstr(self, response):
        return response.count(';') == self.SIZE - 1 or \
            response.count(',') == self.SIZE * (self.SIZE - 1)

    def request_move(self, row, col):
        ''' Sends move to server '''
        self.sock.sendall(''.join([str(row), ',', str(col), self.EOM]))

    def request_newgame(self):
        pass

    def disconnect(self):
        if self.sock:
            if self.connected:
                # in case we haven't recv'd everything server sent.
                # Note: socket.error: [Errno 107] Transport endpoint is
                # not connected if server died a terrible death
                self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        self.connected = False

    def recv_score(self):
        ''' get board state and stats from server'''
        pass

class TUI(object):
    PLAYER_LABELS = {ttt.BSTATES['P1']:'X',
                     ttt.BSTATES['P2']:'O',
                     ttt.BSTATES['EMPTY']:'_'}
    CONNMSGS = {'connect':'Connecting...',
                'waiting': 'Connected. Awaiting partner.',
                'insession': 'Connected. You are',
                'failed': 'Connection failed.'}
    TURNMSGS = {'partner': "Partner's turn.",
                'you': 'Your turn.'}
    HELPMSG = ('\nh - help\n'
               'q - quit\n'
               'm - make move with row col, e.g. m 0 2 is top-right\n'
               'n - new game with same opponent\n')
    PROMPT = '\r>> '

    def __init__(self):
        self.client = TTTClient()

    def process_input(self):
        ''' Responds to commands '''
        while True:
            print self.PROMPT,
            cmd = sys.stdin.readline().strip().lower()
            if cmd == 'h':
                print self.HELPMSG
            elif cmd == 'q':
                self.quit()
                break
            elif cmd == 'n':
                # if game in progress: send forfeit, else do nothing
                pass
            elif cmd.startswith('m'):
                try:
                    row, col = self.parse_move(cmd)
                    self.client.request_move(row, col)
                    break
                except ValueError as e:
                    print 'Invalid command. Try h for help. -- ', e
            else:
                print 'INVALID COMMAND'
                print self.HELPMSG

    def quit(self):
        self.client.disconnect()
        print 'Goodbye'
        sys.exit()

    def parse_sessiontype(self):
        ''' Allows user to choose between playing another person or playing
            against ai (or quit)
        '''
        choice = None
        while choice not in ('a', 'p', 'q'):
            print 'Play against (p)erson or (a)i? ',
            choice = sys.stdin.readline().strip()
            if choice == 'q':
                self.quit()
            self.client.sessiontype = choice

    def join_session(self):
        ''' Sets up initial connection. If the process fails, user can choose
            to try again or quit the program. Returns true if successful,
            false otherwise
        '''
        self.CONNMSGS['connect'],
        # Weirdness: allowing interrupt on connect isn't really useful in
        # practice? I was able to stage a slow-connection scenario at some
        # point early on but now I can't reproduce it. In theory, this is
        # relevant if lots of clients try to connect at the same time?
        # But s.listen(5) on server side doesn't behave the way I expect it to.
        self.allow_interrupt(self.client.connect, 'w')
        while not self.client.connected:
            print self.CONNMSGS['failed'],
            choice = None
            while choice not in ('y','n','q'):
                print 'Try again? (y/n/q) ',
                choice = sys.stdin.readline().strip()
            if choice == 'y':
                self.allow_interrupt(self.client.connect, 'w')
            else:
                return False
        print self.CONNMSGS['waiting'],
        self.client.request_session()
        # expect player id and starter-status in response to session request
        self.allow_interrupt(self.client.await_partner, 'r')
        return True

    def playing_loop(self):
        ''' This should be called after parse_sessiontype and join_session
            have succeeded.
        '''
        print "Instructions: play tic tac toe. Here's how:"
        print self.HELPMSG
        if self.client.i_go_first or self.client.sessiontype == 'a':
            self.print_view()
            self.process_input()
        while True:
            self.allow_interrupt(self.client.await_gameupdate, 'r')
            self.print_view()
            self.process_input()



    def parse_move(self, cmd):
        ''' Interprets command of the form 'm 5 6' as a row, col tuple'''
        if not cmd.startswith('m ') or cmd.count(' ') < 2:
            raise ValueError("Move must be of the form 'm row col")
        return tuple([int(i) for i in cmd[2:].split()])


    def print_view(self):
        ''' Displays UI '''
        if self.client.connected:
            print self.CONNMSGS['insession'], (self.PLAYER_LABELS[
                                                    self.client.role])
            # stats/score
            print 'Won, Lost: ', str((0,0))
            print 'Session Type:', self.client.sessiontype
            # summary of opponent's move TODO
            # if self.client.i_go_first:
            #     print self.TURNMSGS['you']
            # else:
            #     print self.TURNMSGS['partner']
            # board state
            # TODO: for early testing
            # translate string sent by server (boardstring)
            print self.pretty_board()
        else:
            print self.CONNMSGS['failed']

    def pretty_board(self):
        ''' Takes string of the from '0,0,0;1,0,1;0,0,0' and prints
        2D board'''
        if not self.client.lastboardstr:
            return "___\n___\n___\n"
        board = ttt.TicTacToeGame.str_to_grid(self.client.lastboardstr)
        prettyboard = ''
        for row in board:
            for i in row:
                if i == ttt.BSTATES['P1']:
                    prettyboard = ''.join([prettyboard, 'X'])
                elif i == ttt.BSTATES['P2']:
                    prettyboard = ''.join([prettyboard, 'O'])
                else:
                    prettyboard = ''.join([prettyboard, '_'])
            prettyboard = ''.join([prettyboard, '\n'])
        return prettyboard

    def allow_interrupt(self, func, mode):
        ''' Allow user to quit while we keep trying a function that
            depends on a response from the server, e.g. give up
            after waiting for a long time for a response.
            `mode` refers to (r)ead or (w)rite: read is for a `func` that
            contains a recv, write is for a connect.
            Returns whatever `func` returns.
        '''
        to_read = [sys.stdin]
        to_write = []
        if mode == 'r':
            to_read.append(self.client.sock)
        elif mode == 'w':
            to_write.append(self.client.sock)
        while True:
            readyr, readyw, _ = select.select(to_read, to_write,[], 60)
            for stream in readyr:
                if stream is self.client.sock:
                    # reading func is responsible for reading everything
                    # it needs in one shot so we can return
                    return func()
                elif sys.stdin.readline().strip() == 'q':
                    self.quit()
            for stream in readyw:
                return func()


def main():
    t = TUI()
    print "Welcome. Hit 'q' any time to quit."
    t.parse_sessiontype()
    if t.join_session():
        t.playing_loop()
    else:
        t.quit()


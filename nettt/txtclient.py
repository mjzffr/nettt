import ttt
import socket
import errno
import sys
import logging
import select

HOST = 'localhost'
PORT = 50000
GSTATES = ttt.GSTATES
BSTATES = ttt.BSTATES

# general log setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('client.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ' +
                              '%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# initalize game after connection?
#game = ttt.TicTacToeGame()
# connected?
# do I have a partner?
# what if partner disconnects?
# which player am i?

class TTTClient(object):
    # end-of-message marker
    EOM = '\n'

    def __init__(self):
        self.sock = None
        self.session_type = 'a'
        self.reset_connection()


    def reset_connection(self):
        ''' Called in __init__ and when peer disconnects. '''
        self.disconnect()
        self.sock = socket.socket()
        self.connected = False
        self.turn = None
        self.role = None
        # (p)erson or (a)i
        # TODO how will GUI know that self.connected is False? Poll for
        # value with after every time local player makes a move?

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

        #TODO improve logging clarity
        try:
            self.sock.connect((HOST,PORT))
            self.connected = True
            self.sock.setblocking(False)
        except socket.gaierror as e:
            logger.info('Socket gaierror' + str(e))
        except socket.error as e:
            if isinstance(e.args,tuple) and e[0] == errno.EISCONN:
               logger.info('Already connected')
               self.connected = True
            raise_surprise(e,[errno.ECONNABORTED,
                                       errno.ECONNREFUSED])

    def request_session(self):
        ''' Asks server for a game and a partner '''
        logger.info('Requested session type' + self.session_type)
        # send type of session (ai or person)
        # expect your player id and turn-status in response
        self.sock.sendall(''.join([self.session_type, self.EOM]))

    def await_partner(self):
        ''' Expecting to receive string of the form 'xx,yy' where xx and yy
        must be +1 or -1 and xx represents client's role and yy represents
        whose turn it is.
        '''
        # TODO: use end of msg marker
        response = self.sock.recv(5)
        logger.info('Response: ' + response)
        errmsg = 'Protocol violated: ' + response
        if len(response) != 5:
            logger.info(errmsg)
            raise Exception(errmsg)
        self.role, self.turn = tuple([int(i) for i in response.split(',')])
        if self.role not in [1, -1] or self.turn not in [1, -1]:
            logger.info(errmsg)
            raise Exception(errmsg)

    def request_status(self): #I don't remember what this is for :(
        pass

    def request_move(self):
        pass

    def request_newgame(self):
        pass

    def disconnect(self):
        if self.sock:
            if self.connected:
                # in case we haven't recv'd everything server sent
                # Note: socket.error: [Errno 107] Transport endpoint is
                # not connected if server died a terrible death
                self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        self.connected = False

    def recv_update(self):
        ''' get board state and stats from server'''
        pass

class TUI(object):
    PLAYER_LABELS = {BSTATES['P1']:'X',
                     BSTATES['P2']:'O',
                     BSTATES['EMPTY']:'_'}
    CONNMSGS = {'connect':'\rConnecting...',
                'waiting': '\rConnected. Awaiting partner.',
                'insession': '\rConnected. You are ',
                'failed': '\rConnection failed.'}
    TURNMSGS = {'partner': "\rPartner's turn.",
                'you': '\rYour turn.'}
    HELPMSG = ('\nh - help\n'
               'q - quit\n'
               'm - make move with row col, e.g. m 0 2 is top-right\n'
               'n - new game with same opponent\n')
    PROMPT = '\r>> '

    def __init__(self):
        self.client = TTTClient()
        # TODO: for early testing
        self.tempgame = ttt.TicTacToeGame()

    def parse_playinput(self, rawcmd):
        ''' responds to commands '''
        cmd = rawcmd.strip().lower()
        if cmd == 'h':
            print self.HELPMSG
        elif cmd == 'q':
            self.quit()
        elif cmd == 'n':
            # if game in progress send forfeit, else do nothing
            pass
        elif cmd.startswith('m'):
            try:
                self.parse_move(cmd)
            except ValueError as e:
                print '\rInvalid command. Try h for help. -- ', e
        else:
            print 'INVALID COMMAND'
            print self.HELPMSG

    def quit(self):
        self.client.disconnect()
        print '\rGoodbye'
        sys.exit()

    def parse_sessiontype(self):
        ''' User can choose between playing another person or playing
            against ai
        '''
        choice = None
        while choice not in ('a', 'p', 'q'):
            print '\rPlay against (p)erson or (a)i? ',
            choice = sys.stdin.readline().strip()
            if choice == 'q':
                self.quit()
            self.client.session_type = choice

    def join_session(self):
        ''' User can choose to try again to join or quit the
            program.
            Returns true if successful, false otherwise
        '''
        self.CONNMSGS['connect'],
        # allowing interrupt on connect isn't really useful in practice?
        # maybe if lots of clients try to connect at the same time?
        # I can't seem to reproduce that scenario :(
        self.allow_interrupt(self.client.connect, 'w')
        # retry
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
        self.allow_interrupt(self.client.await_partner, 'r')
        return True

    def playing_loop(self):
        ''' This should be called after choose_session_type and
            join_session have succeeded.
        '''
        print "Instructions: play tic tac toe. Here's how:"
        print self.HELPMSG
        while True:
            self.print_view()
            self.parse_playinput(sys.stdin.readline().strip())

    def parse_move(self, cmd):
        # cmd is of the form 'm 5 6'
        if not cmd.startswith('m ') or cmd.count(' ') != 2:
            raise ValueError("Move must be of the form 'm row col")
        row, col = tuple([int(i) for i in cmd[2:].split()])
        # TODO: for early testing
        self.tempgame.make_move(1, (row,col))

    def print_view(self):
        # connection status - Connected. You are X
        if self.client.connected:
            print self.CONNMSGS['insession'], self.client.role
            # stats/score
            print 'Won, Lost: ', str((0,0))
            print 'Session Type: ', self.client.session_type
            # summary of opponent's move TODO
            if self.client.turn == self.client.role:
                print self.TURNMSGS['you']
            else:
                print self.TURNMSGS['partner']
            # board state
            # TODO: for early testing
            print self.tempgame
        else:
            print '\r', self.CONNMSGS['failed']
        print self.PROMPT,

    def allow_interrupt(self, func, mode):
        ''' Allow user to quit while we keep trying a function that
            depends on response from server, e.g. give up
            after waiting for a long time for a response.
            mode refers to (r)ead or (w)rite: read is for recv, write
            is for connect.
            '''
        # Note, join_session is implemented differently because we want
        # the client to try one and then always give the user to try
        # again or give up.
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
                    # it needs in one shot so we can return?
                    print "before"
                    func()
                    print "here"
                    return
                elif sys.stdin.readline().strip() == 'q':
                    self.quit()
            for stream in readyw:
                print "writer"
                func()
                return




def main():
    t = TUI()
    print "Welcome. Hit 'q' any time to quit."
    t.parse_sessiontype()
    if t.join_session():
        t.playing_loop()
    else:
        t.quit()


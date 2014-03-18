import ttt
import socket
import errno
import sys

HOST = 'localhost'
PORT = 50000
GSTATES = ttt.GSTATES
BSTATES = ttt.BSTATES


# initalize game after connection?
#game = ttt.TicTacToeGame()
# connected?
# do I have a partner?
# what if partner disconnects?
# which player am i?

class TTTClient(object):
    def __init__(self):
        self.s = None
        self.reset_connection()

    def reset_connection(self):
        ''' Called at beginning and when peer disconnects. '''
        if self.s:
            self.s.close()
        self.s = socket.socket()
        self.s.settimeout(30)
        self.connected = False
        self.partner = None
        # TODO how will GUI know that self.connected is False? Poll for
        # value with after every time local player makes a move?

    def connect(self, attempts=10):
        if self.connected:
            return

        for i in range(attempts):
            print 'Attempt', i,
            try:
                self.s.connect((HOST,PORT))
                self.connected = True
                break
            except socket.timeout as e:
                print 'Socket Timeout', e
            except socket.gaierror as e:
                print 'Socket gaierror', e
            except socket.error as e:
                if isinstance(e.args,tuple) and e[0] == errno.EISCONN:
                   print 'Already connected'
                   self.connected = True
                   break
                TTTClient.raise_surprise(e,[errno.ECONNABORTED,
                                           errno.ECONNREFUSED])

    @staticmethod
    def raise_surprise(e, errcodes):
        ''' Propagates exception e if it doesn't match any errcodes '''
        if isinstance(e.args,tuple) and any([e[0] == c for c in errcodes]):
            # we were expecting this one
            print e
        else:
            # surprise!
            raise e


    def establish_session(self):
        #while not self.partner:
        print 'establish'
        self.partner = self.s.recv(8)
            #self.role = self.s.recv(8)

    def ask_status(self):
        pass

    def send_move(self):
        pass

    def send_newgame(self):
        pass

    def end_session(self):
        if self.connected:
            self.s.close()
        self.connected = False
        pass

    def recv_update(self):
        pass

class TUI(object):
    PLAYER_LABELS = {BSTATES['P1']:'X',
                     BSTATES['P2']:'O',
                     BSTATES['EMPTY']:'_'}


    CONNMSGS = {'connect':'Connecting...',
                'waiting': 'Connected. Awaiting partner.',
                'insession': 'Connected. You are',
                'failed': 'Connection failed.'}

    TURNMSGS = {'partner': "Partner's turn.",
                'you': 'Your turn.'}

    def __init__(self):
        self.client = TTTClient()
        self.tempgame = ttt.TicTacToeGame()

    def parse_input(self, rawcmd):
        helpmsg = ('\nh - help\n'
                   'q - quit\n'
                   'c - reconnect to server\n'
                   'm - make move with xcoord ycoord, e.g. m 0 0 is top-left\n'
                   'n - new game\n')
        cmd = rawcmd.strip().lower()
        if cmd == 'h':
            print helpmsg
        elif cmd == 'q':
            self.quit()
        elif cmd == 'c':
            client.reset_connection()
        elif cmd == 'n':
            # if game in progress send forfeit, else do nothing
            pass
        elif cmd.startswith('m'):
            pass
        else:
            print 'INVALID COMMAND'
            print helpmsg

    def quit(self):
        self.client.end_session()
        print '\rGoodbye'
        sys.exit()

    def play(self):
        while True:
            self.print_view()
            self.parse_input(sys.stdin.readline().strip())

    def print_view(self):
         # connection status - Connected. You are X
        print '\r', self.CONNMSGS['connect']
        # stats/score
        print 'Won, Lost: ', str((0,0))
        # summary of opponent's move TODO
        # turn - Your Turn TODO
        # print self.TURNMSGS['you']
        # board state
        print self.tempgame
        # prompt
        print '>> ',


def main():
    TUI().play()

if __name__ == '__main__':
    main()

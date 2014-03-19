import ttt
import socket
import errno

HOST = 'localhost'
PORT = 50000

GSTATES = ttt.GSTATES
BSTATES = ttt.BSTATES
# initalize game after connection?
game = ttt.TicTacToeGame()
# connected?
# do I have a partner?
# what if partner disconnects?
# which player am i?

class TTTClient:
    def __init__(self):
        self.s = None
        self.reset_connection()

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


    def send_move(self):
        pass

    def send_forfeit(self):
        pass

    def end_session(self):
        self.s.close()
        self.connected = False
        pass

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

    def recv_update(self):
        pass



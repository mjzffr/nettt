import ttt
import socket

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
    def __init__(self, attempts = 10):
        self.partner = None
        self.connected = False
        self.s = socket.socket()
        self.s.settimeout(10)

        for i in range(attempts):
            try:
                self.s.connect((HOST,PORT))
                self.connected = True
                break
            except socket.timeout as e:
                print 'Socket Timeout', e, 'Attempt', i
            except socket.gaierror as e:
                print 'Socket gaierror', e, 'Attempt', i
            except socket.error as e:
                print 'Socket Error', e, 'Attempt', i
            except:
                print 'Unexpected error', e, 'Attempt:', i

        print self.connected


    def establish_session(self):
        #while not self.partner:
            #self.partner = fromserver
            #self.role = fromserver
            pass

    def send_move(self):
        pass

    def send_forfeit(self):
        pass

    def end_session(self):
        self.s.close()
        pass

    def recv_update(self):
        pass



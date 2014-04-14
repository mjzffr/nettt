#!/usr/bin/env python2
import random

BSTATES = {'EMPTY':0, 'P1':1, 'P2':-1}
GSTATES = {'INPROGRESS':4, 'NOTSTARTED':3, 'P2WON':BSTATES['P2'],
                        'P1WON':BSTATES['P1'], 'DRAW':2}

class TicTacToeGame:
    ''' State consists of two players, board state, game mode (in progress,
        draw, etc), num games won/lost by each player, last winning coordinates
        Can generate computer moves; represent board state as a string; record
        plays actions (move, reset) and their effects.
    '''
    def __init__(self, size=3, initial_state=None, first=BSTATES['P1']):
        self.SIZE = size
        self.board = [[BSTATES['EMPTY']] * self.SIZE for _ in range(self.SIZE)]

        self.current_player = first
        self.mode = GSTATES['NOTSTARTED']

        self.wins = {BSTATES['P1']:0, BSTATES['P2']:0}
        self.losses = {BSTATES['P1']:0, BSTATES['P2']:0}

        self.lastwincoords = set()

        # for testing
        if initial_state:
            self.board = initial_state

    @property
    def board_1d(self):
        ''' 1D list representing game board1'''
        return [i for row in self.board for i in row]

    @property
    def boardstr(self):
        ''' String representation of game board
            XO_  is represented as  '1,-1,0;0,-1,1;0,0,1'
            _OX
            __X
        '''
        # more general than necessary (from before this was a property)
        if not TicTacToeGame.is_square(self.board):
            raise ValueError('The grid must be n x n')
        size = len(self.board)

        rowstrs = [','.join([str(i) for i in row]) for row in self.board]
        # format howto: {} is replaced by item of l
        return ('{};' * (size - 1) +'{}').format(*rowstrs)

    def make_random_move(self, player):
        ''' player is 1 or -1 (for X or O)
            in addition to updating board, returns the location that was changed
        '''

        location = random.choice(self.get_locations(self.board,
                                 BSTATES['EMPTY']))
        return self.make_move(player, location)


    @staticmethod
    def get_locations(board, bstate):
        ''' returns list of (row, col) tuples at which the board state is
         bstate '''
        return [(ri,ci) for ri,row in
                enumerate(board) for ci,spot in
                enumerate(row) if spot == bstate]

    @property
    def is_over(self):
        #print "Check %s" % self.mode
        return self.mode <= 2
        #return self.mode in (GSTATES['XWon'], GSTATES['OWon'],GSTATES['Draw'])


    def reset(self, player):
        ''' updates game state in response to player asking for a new
        game
        '''
        if self.mode == GSTATES['INPROGRESS']:
            self.losses[player] += 1
            self.wins[player * -1] += 1
        self.board = [[BSTATES['EMPTY'] for i in range(self.SIZE)] \
                   for i in range(self.SIZE)]
        self.current_player = BSTATES['P1']
        self.mode = GSTATES['NOTSTARTED']

    def make_move(self, player, (row, col)):
        ''' player is 1 or -1 (for X or O)
            in addition to updating board, also returns location that was
            changed. Returns None if the game is over (move didn't work)
        '''
        if self.is_over:
            return
        # validate
        size = self.SIZE
        if player != self.current_player:
            msg = ("Invalid player " + str(player) + ". Should be " +
                    str(self.current_player))
            raise ValueError(msg)
        if row not in range(size) or col not in range(size):
            raise ValueError("Invalid location value " + str((row, col)))

        # update state
        if self.board[row][col] == BSTATES['EMPTY']:
            self.board[row][col] = player
            self.update_mode()
            #print self.mode
            if self.mode == GSTATES['INPROGRESS']:
                # only switch turns if most recent move did not end the game
                self.current_player *= -1
        else:
            raise ValueError("Location already full " + str((row, col)))
        #print self
        #print

        return (row, col)

    def update_score(self):
        ''' increments number of wins/losses for each player'''
        if self.mode == GSTATES['P1WON']:
            self.wins[BSTATES['P1']] += 1
            self.losses[BSTATES['P2']] += 1
        elif self.mode == GSTATES['P2WON']:
            self.wins[BSTATES['P2']] += 1
            self.losses[BSTATES['P1']] += 1


    def update_mode(self):
        ''' updates game mode (in progress, won, etc) according to current
         state of board '''
        s = self.SIZE

        # don't check until one player has made > size moves
        if self.board_1d.count(BSTATES['EMPTY']) > s ** 2 - (s * 2 - 1):
            self.mode = GSTATES['INPROGRESS']
            return

        self.mode, resultcoords = \
            TicTacToeGame.decide_mode(self.board)
        self.update_score()

        # <= 2 means draw, xwon or owon
        if self.is_over:
            self.lastwincoords = resultcoords


    # TODO: testing
    @staticmethod
    def is_winning_line(line):
        ''' return true if line consists of all 'X' or 'O';
        line is a list of board space values, like a row or a diagonal'''
        return BSTATES['EMPTY'] not in line and all(line[0] == i for i in \
                                                      line)

    @staticmethod
    def decide_mode(board):
        ''' return pair of gstate and set of winning line coords if there
            is one
        '''
        s = len(board)

        for ri,rowvals in enumerate(board):
            if TicTacToeGame.is_winning_line(rowvals):
                return (rowvals[0], set([(ri,i) for i in range(s)]))
        for ci,colvals in enumerate(zip(*board)):
            if TicTacToeGame.is_winning_line(colvals):
                return (colvals[0], set([(i,ci) for i in range(s)]))

        diagonal_coords = [[(i,i) for i in range(s)],
            [(s - 1 - i, i) for i in range(s)]]
        diagonals = [[board[i][i] for i in range(s)],
            [board[s - 1 - i][i] for i in range(s)]]

        for i,diagvals in enumerate(diagonals):
            if TicTacToeGame.is_winning_line(diagvals):
                return (diagvals[0], set(diagonal_coords[i]))

        board_1d = [i for row in board for i in row]
        if BSTATES['EMPTY'] not in board_1d:
            return (GSTATES['DRAW'], set())

        #otherwise
        return (GSTATES['INPROGRESS'], set())


    ''' Helper funcions for compact string representation of game board

    XO_  is represented as  '1,-1,0;0,-1,1;0,0,1'
    _OX
    __X

    '''

    @staticmethod
    def str_to_grid(stringrep):
        ''' returns n by n list given string of the form
        '1,-1,0;0,-1,1;0,0,1'
        '''
        return [map(int,i.split(',')) for i in stringrep.split(';')]

    @staticmethod
    def str_to_list(stringrep):
        ''' returns 1d list given string of the form '1,-1,0;0,-1,1;0,0,1'
        '''
        return TicTacToeGame.grid_to_list(TicTacToeGame.str_to_grid(stringrep))

    @staticmethod
    def is_square(grid):
        ''' true if grid is n x n list '''
        return all([len(grid) == len(i) for i in grid])

    # for testing
    def __str__(self):
        boardstr = ''
        for row in self.board:
            for i in row:
                if i == BSTATES['P1']:
                    boardstr = ''.join([boardstr, 'X'])
                elif i == BSTATES['P2']:
                    boardstr = ''.join([boardstr, 'O'])
                else:
                    boardstr = ''.join([boardstr, '_'])
            boardstr = ''.join([boardstr, '\n'])
        return boardstr

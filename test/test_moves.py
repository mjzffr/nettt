import pytest
from nettt import ttt
#import shared_data as shared


# @pytest.fixture(params=shared.initstates)
# def initialized_game(request):
#     ''' a game that starts in a particular state config '''
#     g = ttt.TicTacToeGame(initial_state=request.param)
#     g.update_mode()
#     return g

def setup_game(state):
    g = ttt.TicTacToeGame(initial_state=state)
    g.update_mode()
    return g

@pytest.fixture
def game():
    return ttt.TicTacToeGame()


@pytest.fixture
def p2_game():
    g = setup_game([[-1, 0, 0],
                   [-1, 1, 0],
                   [1, 0, 1]])
    g.current_player = -1
    return g

@pytest.fixture
def done_game():
    return setup_game([[-1, 1, 0],
                       [-1, 1, 0],
                       [-1, 0, 1]])

moves = [   (1, (1,0)),
            (-1, (0,2)),
            (1, (0,1)),
            (-1, (1,2)),
            (1, (0,0))
        ]

def test_first_player(game):
    assert game.current_player == ttt.BSTATES['P1']

def test_occupied_location(p2_game):
     with pytest.raises(ValueError) as excinfo:
        p2_game.make_move(1, (0,0))

def test_single_move_coord(game):
    game.make_move(1, (1, 2))
    assert game.board == [[0, 0, 0], [0, 0, 1], [0, 0, 0]]

def test_single_move_coord(game):
    game.current_player = -1
    game.make_move(-1, (2, 0))
    assert game.board == [[0, 0, 0], [0, 0, 0], [-1, 0, 0]]

def test_game_over(done_game):
    with pytest.raises(Exception):
        done_game.make_move(1, (0,2))

def test_wrong_player(p2_game):
    with pytest.raises(ValueError):
        p2_game.make_move(1, (0,2))

def test_invalid_location(game):
    with pytest.raises(ValueError):
        game.make_move(1, (3,3))

def test_sequences_of_moves(game):
    for m in moves:
        game.make_move(m[0], m[1])
    assert game.board == [[1, 1, -1], [1, 0, -1], [0, 0, 0]]

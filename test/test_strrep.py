from nettt import ttt
import pytest
import shared_data as shared


# @pytest.fixture(scope="module")
# def game():
#     return ttt.TicTacToeGame()

# from https://pytest.org/latest/example/parametrize.html
# For every k,v in 'params' dictionary, gives parameters v to function k
def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.module.params[metafunc.function.__name__]
    argnames = list(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames]
            for funcargs in funcarglist])

strreps = ['0,0,1;-1,1,1;-1,1,-1',
       '1,1,-1;-1,1,1;1,-1,-1',
       '1,0,0;0,1,0;0,1,0',
       '1,-1,0;0,1,-1;0,0,1',
       '-1,0,0;-1,1,0;-1,0,1',
       '-1,-1,1;1,1,-1;0,-1,0',
       '-1,-1,-1;1,1,0;1,0,1']

state_rep = [dict(state=s, rep=r) for s,r in zip(shared.initstates,strreps)]
sizes = [dict(testsize=s) for s in range(2,8)]
dimensions = [dict(w=5, h=2)]
# a map specifying multiple argument sets for a test method
# Used by pytest_generate_tests
params = { 'test_to_srepr': state_rep,
            'test_diff_size_srepr': sizes,
            'test_str_to_grid': state_rep,
            'test_to_srepr_fail': dimensions}

def test_to_srepr(state, rep):
    assert ttt.TicTacToeGame.to_srepr(state) == rep

def test_diff_size_srepr(testsize):
    s = testsize
    i = s/2
    g = ttt.TicTacToeGame(size=s)
    state = [[0] * s for j in range(s)]
    state[i][0] = -1
    zeros = ((('0,'*s)[:-1]+';')*s)[:-1]
    target = zeros[:s*2*(i)]+'-1'+zeros[s*2*(i)+1:]

    assert ttt.TicTacToeGame.to_srepr(state) == target

def test_str_to_grid(state, rep):
    assert ttt.TicTacToeGame.str_to_grid(rep) == state

def test_to_srepr_fail(w, h):
    notsquare = [[0]*w for i in range(h)]
    with pytest.raises(ValueError):
        ttt.TicTacToeGame.to_srepr(notsquare)


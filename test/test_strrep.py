from nettt import ttt
import pytest
import shared_data as shared

strreps = ['0,0,1;-1,1,1;-1,1,-1',
           '1,1,-1;-1,1,1;1,-1,-1',
           '1,0,0;0,1,0;0,1,0',
           '1,-1,0;0,1,-1;0,0,1',
           '-1,0,0;-1,1,0;-1,0,1',
           '-1,-1,1;1,1,-1;0,-1,0',
           '-1,-1,-1;1,1,0;1,0,1']

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

state_rep = [dict(state=s, rep=r) for s,r in zip(shared.initstates,strreps)]


# a map specifying multiple argument sets for a test method
# Used by pytest_generate_tests
params = {  'test_to_srepr': state_rep }

def test_to_srepr(state, rep):
    assert ttt.TicTacToeGame().to_srepr(state) == rep

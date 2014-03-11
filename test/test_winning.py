#!/usr/bin/env python2
import pytest
from nettt import ttt
import shared_data as shared

GSTATES = ttt.GSTATES

initstates = shared.initstates

modes =  [  GSTATES['INPROGRESS'],
            GSTATES['DRAW'],
            GSTATES['INPROGRESS'],
            GSTATES['P1WON'],
            GSTATES['P2WON'],
            GSTATES['INPROGRESS'],
            GSTATES['P2WON']]

lines =  [  [],
            [],
            [],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [],
            [(0, 0), (0, 1), (0, 2)]]

# from https://pytest.org/latest/example/parametrize.html
# For every k,v in 'params' dictionary, gives parameters v to function k
def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.module.params[metafunc.function.__name__]
    argnames = list(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames]
            for funcargs in funcarglist])

state_mode = [dict(state=s, mode=m) for s,m in zip(initstates,modes)]

state_line = [dict(state=s, line=set(l)) for s,l in zip(initstates,lines)]

# a map specifying multiple argument sets for a test method
# Used by pytest_generate_tests
params = {  'test_modes': state_mode,
            'test_lines': state_line }

def test_modes(state, mode):
    g = ttt.TicTacToeGame(initial_state=state)
    g.update_mode()
    print g
    assert g.mode == mode

def test_lines(state, line):
    g = ttt.TicTacToeGame(initial_state=state)
    g.update_mode()
    print g
    assert g.lastwincoords == line

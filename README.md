nettt
=====
Work in progress. 

A networked version of tittertactoe to practice socket programming in python. Yay!

## Goal

While the server (`nettt_server.py`) is running, several clients can connect and interact with each other by playing games of tic tac toe.

## Current state

There are two UIs for the client side: `nettt_gui.py` and `txtclient.py`. I'm nolonger developing the GUI for now because my priority is to get comfortable with socket programming, rather than think about how to have tkinter interact with sockets. (Twisted?) So the focus for now is on `txtclient.py`. 

What works so far: 

* The user can join a "session" and that session can either be with another human player or a computer. 
* The user can send moves to play against the server's ai or another human
* Waiting for server response does not block the game: you can quit at any time.
* If one player quits, his partner is kicked off and the session is deleted.

What doesn't work yet:
* The client/server are not fully hooked up with the game logic. Examples:
    * end-of-game occurs: server sends info that game is over, but client can't start new game or receive his game stats (score)
    * client sends illegal move: server sends error and client responds by crashing
    * client moves out-of-turn: the client code doesn't allow this, but if it did, the server would just crash

## How to run

You probably need to use Linux because I don't think Windows likes it when we use `select` on `stdin`. It's probably fine on Mac OS, but if you run the GUI it will look very weird.

Install the requirements first: `pip install -r requirements.txt` (Optional, unless you want to run the tests.)

* Start the server: `./nettt_server.py`
* Start a client: `python nettt` where `nettt` is the directory that contains `__main__.py` This will run the text-based UI.

## Tests

The tests are for fun.  

To run the tests: `py.test` from project root directory. It is assumed that the tittertactoe package is "importable" in the current virtual environment (i.e. `pip install -e .` in project root) as per these guidelines: https://pytest.org/latest/goodpractises.html#choosing-a-test-layout-import-rules 


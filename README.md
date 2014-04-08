nettt
=====
Work in progress. 

A networked version of tittertactoe to practice socket programming in python. Yay!

## Goal

While the server (`nettt_server.py`) is running, several clients can connect and interact with each other by playing games of tic tac toe.

## Current state

There are two UIs for the client side: `nettt_gui.py` and `txtclient.py`. I'm nolonger developing the GUI for now because I don't want to figure out how to have tkinter interact with sockets. So the focus for now is on `txtclient.py`. So far, all that works is that a player can join a "session" and that session can either be with another human player or a computer. The sending of moves/receiving of updates is not implemented yet.

## How to run

Install the requirements first: `pip install -r requirements.txt` (Optional, unless you want to run the tests.)

* Start the server: `./nettt_server.py`
* Start a client: `python nettt` where `nettt` is the directory that contains `__main__.py` This will run the text-based UI.

## Tests

The tests are for fun.  

To run the tests: `py.test` from project root directory. It is assumed that the tittertactoe package is "importable" in the current virtual environment (i.e. `pip install -e .` in project root) as per these guidelines: https://pytest.org/latest/goodpractises.html#choosing-a-test-layout-import-rules 


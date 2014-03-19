nettt
=====
Work in progress. 

A networked version of tittertactoe to practice socket programming in python. Yay!

## Goal

While the server (`nettt_server.py`) is running, several clients can connect and interact with each other by playing games of tic tac toe.

## Current state

There are two UIs for the client side: `nettt_gui.py` and `txtclient.py`. I'm nolonger developing the GUI for now because I don't want to figure out how to have tkinter interact with sockets. So the focus for now is on `txtclient.py`. Nothing really works yet.

## How to run

Install the requirements first: `pip install -r requirements.txt`

* Server: `./nettt_server.py`
* Client: `python nettt` where `nettt` is the directory that contains `__main__.py` This will run the text-based UI.

## Tests

The tests are for fun.  

To run the tests: `py.test` from project root directory. It is assumed that the tittertactoe package is "importable" in the current virtual environment (i.e. `pip install -e .` in project root) as per these guidelines: https://pytest.org/latest/goodpractises.html#choosing-a-test-layout-import-rules 


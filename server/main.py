"""
Python 3.10 is needed
Execute "pip install bcrypt" before running the server
The main file of the server to allow clients to connect to the server
~ Hartl Lorenz, Hell Andreas, Holas Christoph
"""

from server_network import *
import database


if __name__ == "__main__":
    db = database.Database()
    server = NetworkServer()
    
    server.accept_clients(db)
    db.close_conn()
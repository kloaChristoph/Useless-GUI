from server_network import *
import database


if __name__ == "__main__":
    db = database.Database()
    server = NetworkServer(db)
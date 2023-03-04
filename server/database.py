import sqlite3
import bcrypt

class Database:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("useless_gui.db")
        self.cursor = self.conn.cursor()

        
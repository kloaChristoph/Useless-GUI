import sqlite3
import bcrypt

class Database:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("useless_gui.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            highscore INTEGER,
            accuracy FLOAT,
            time INTEGER)
        """)

    def register_user(self, username, password) -> bool:
        self.cursor.execute("INSERT INTO accounts (username, password, highscore, accuracy, time) VALUES (?, ?, ?, ?, ?)", (username, password, 0, 0, 30))
        self.conn.commit()
    

    def verify_user(self, username:str, password:str):
        """
        Checks if the user entered the correct password 

        Parameters
        ----------
        username : str
            The name of the user who is trying to log in
        password : str
            The password the user entered

        Returns
        -------
        successful_login : bool
            Returns if the password was correct
        """
        self.cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
        db_entry = self.cursor.fetchone()
        if db_entry:
            db_password = db_entry[0]
            successful_login = bcrypt.checkpw(password.encode(), db_password)
            return successful_login
        else:
            return False
        

if __name__ == "__main__":
    db = Database()
    
    db.register_user("admin", bcrypt.hashpw("admin".encode(), bcrypt.gensalt()))
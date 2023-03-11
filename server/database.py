"""
In this file the database is created and the functions to access the database are defined
~ Hartl Lorenz, Hell Andreas, Holas Christoph
"""

import sqlite3
import bcrypt

class Database:
    """
    A class to handle the database

    ...

    Attributes
    ----------
    conn : sqlite3.Connection
        The connection to the database
    cursor : sqlite3.Cursor
        The cursor to execute SQL commands

    Methods
    -------
    register_user(username: str, password: str) -> bool
        Checks if there is already a user with the given name if not: stores new account in the database
    verify_user(username:str, password:str) -> bool
        Checks if the user entered the correct password
    updat_highscore(uesrname: str, highscore: int, accuracy: float, time: int) -> None
        Updates the highscore of the user
    get_highscores() -> list[list[float, str, int, float, int]]
        Gets the highscores of all players and returns the top 10
    close_conn() -> None
        Closes the connection to the database
    """

    def __init__(self) -> None:
        """
        Initialize the database and creates the table if it doesn't exist

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
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


    def register_user(self, username: str, password: str) -> bool:
        """
        Checks if there is already a user with the given name
        if not: stores new account in the database

        Parameters
        ----------
        username : str
            The name of the user who is trying to register
        password : str
            The password the user entered

        Returns
        -------
        : bool
            Returns if the registration was successful
        """
        self.cursor.execute("SELECT username FROM accounts WHERE username = ?", (username,))
        db_entry = self.cursor.fetchone()
        if db_entry:
            db_username = db_entry[0]
            if db_username == username:
                return False
        
        else:
            db_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            self.cursor.execute("INSERT INTO accounts (username, password, highscore, accuracy, time) \
                                VALUES (?, ?, ?, ?, ?)", (username, db_password, 0, 0, 30))
            self.conn.commit()
            return True
 

    def verify_user(self, username:str, password:str) -> bool:
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
        

    def updat_highscore(self, uesrname: str, highscore: int, accuracy: float, time: int) -> None:
        """
        Updates the highscore of the user

        Parameters
        ----------
        username : str
            The name of the user who is trying to log in
        highscore : int
            The new highscore of the user
        accuracy : float
            The accuracy the user had at his highscore
        time : int
            The time the user had to reach the highscore

        Returns
        -------
        None
        """
        self.cursor.execute("UPDATE accounts SET highscore = ?, accuracy = ?, time = ? \
                            where username = ?", (highscore, accuracy, time, uesrname))
        self.conn.commit()
 

    def get_highscores(self) -> list[list[str, float, int, float, int]]:
        """
        Gets the highscores of all players and returns the top 10

        Parameters
        ----------
        None

        Returns
        -------
        sorted_highscores : list[list[str, float, int, float, int]]
            The top 10 clients in a sorted list (best is index 0) with their name, rating, score, accuracy and time
        """
        self.cursor.execute("SElECT username, highscore, accuracy, time from accounts")
        db_entry = self.cursor.fetchall()
        highscores = []
        if db_entry:
            for entry in db_entry:
                name, score, accuracy, time = entry
                avg_score_per_sec = round((score*accuracy)/(100*time), 3)
                highscores.append([name, avg_score_per_sec, score, accuracy, time])

            sorted_highscores = sorted(highscores, key= lambda client: client[1], reverse=True)
            return sorted_highscores[0:10]

    
    def get_user_highscore(self, username: str) -> list[float, int, float, int]:
        """
        Gets the highscore of the user

        Parameters
        ----------
        username : str
            The name of the user who requests his highscore

        Returns
        -------
        highscore : list[float, int, float, int]
            The highscore of the user
        """
        self.cursor.execute("SElECT highscore, accuracy, time from accounts where username = ?", (username,))
        db_entry = self.cursor.fetchone()
        if db_entry:
            score, accuracy, time = db_entry
            avg_score_per_sec = round((score*accuracy)/(100*time), 3)
            highscore = [avg_score_per_sec, score, accuracy, time]
            return highscore
        else:
            return None


    def close_conn(self) -> None:
        """
        Closes the connection to the database

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.conn.close()



if __name__ == "__main__":
    db = Database()
    
    #db.register_user("admin", "admin")
    db.updat_highscore("admin", 13, 94.2, 10)
    db.updat_highscore("christoph", 16, 83.8, 10)

    #db.get_highscores()
    #db.get_user_highscore("admin")
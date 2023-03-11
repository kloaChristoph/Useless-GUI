"""
In this file the class of the App and the GameButton is 
~ Hartl Lorenz, Hell Andreas, Holas Christoph
"""

import tkinter
import tkinter.messagebox
from tkinter import ttk
import random
import time
from client_network import NetworkClient

class App:
    """
    A class to handle the window ant the game

    ...

    Attributes
    ----------
    client : NetworkClient
        The network part of the client
    window : tkinter.TK
        The window which is shown to the user
    username : str
        The name of the user

    login_status : bool
        A variable to check the if user is loged in 
    game_running : bool
        A variable to check if there is a game running

    score: int
        The score of the last game
    missed_cliscks: int
        The wrong presses of the last game
    accuracy : float
        The calculated accuracy the user had in the last game [%]
    highscore : int 
        The all time highscore of the user
    highscore_accuracy : float
        The accuracy the user had when reaching the highscore
    rating : float
        The ratinf of th last game (is used to compare the highscore)
    highest_rating : float
        The highest rating the user had all time

    exit_button : tkinter.Button
        Sends the server a command to close the connection if loged in and closes the window (calls exit_app)
    start_button : tkinter.Button
        Starts a new game if there is no game running (calls start_game)
    time_label : tkinter.Label
        Show the time which is left in the game
    login_button : tkinter.Button
        Tries to log in (calls login)
        Shows login screen if user is in register screen (calls login_window)
    register_button : tkinter.Button
        Tries to register and log in (calls register)
        Shows register screen if user is in login screen (calls register_window)
    username_label : tkinter.Label
        Shows where to type the username in the login/register window
    username_entry : tkinter.Entry
        Allows the user to type in the username in the login/register window
    password_label : tkinter.Label
        Shows where to type the password in the login/register window
    password_entry : tkinter.Entry
        Allows the user to type in the username in the login/register window
    password_confirm_label : tkinter.Label
        Shows where to confirm the typed password in the register window
    password_confirm_entry : tkinter.Entry
        Allows the user to conf
    highscore_talbe : ttk.Treeview
        The table to show the highscores of the top 10 users
    buttons : list[GameButton]
        A list of the game buttons (each calls GameButton.check_status)
    
    Methods
    -------
    start_loop() -> None
        Starts the mainloop to update the window
    handle_server_commands() -> None
        Handle the commands received from the server
    login_window() -> None
        Changes the Window to the login screen
    login() -> None
        Method triggerd by the login button when user is in the login screen
        Calls the setup_connection method and destroys the widgets that are no longer needed
    register_window() -> None
        Changes the Window to the register screen
    register() -> None
        Method triggerd by the register button when user is in the register screen
        Calls the setup_connection method and destroys the widgets that are no longer needed
        The user is loged in automatically
    setup_connection(register: bool) -> None
        Tries to connect to server and gives pop up if connection to server failed or the login wasn't correct
    start_game() -> None
        Starts the game if there is no game running
        Is triggert by the start button in the main window
    show_end_msg() -> None
        Shows a pop up at the end of the game
        Shows the reached score and if it is a new highscore
    create_table() -> None
        Creats the highscore table
    update_highscore_table(data: dict) -> None
        Updates the highscore table
    show_buttons() -> None
        Creating and showing the buttons needed for the game
    calculate_stats() -> None
        Calculates the stats of the last game
    reset_stats() -> None
        Resets the current game stats
    exit_app() -> None
        Show pop up if user really want's to exit the app
        Sends the server a command to close the connection
        Closes the window
    """

    def __init__(self, window: tkinter.Tk, window_title: str) -> None:
        """
        Initialize a new App

        Parameters
        ----------
        window : tkinter.TK
            The window to show the app
        window_title : str
            The name of the Window

        Returns
        -------
        None
        """
        self.client = NetworkClient()

        self.window: tkinter.Tk = window
        self.login_status: bool = False
        self.username: str = ""

        self.exit_button = tkinter.Button(self.window, name="exit_button", text="Exit", command=self.exit_app, height=2, width=10)
        self.exit_button.place(x=400, y=350)

        self.login_window()

        self.window.title(window_title)
        self.window.geometry("700x500")
        self.game_running: bool = False
        self.duration: int = 10
        self.score: int = 0
        self.missed_clicks: int = 0
        self.accuracy: float = 100
        self.highscore: int = 0
        self.highscore_accuracy: float = 0
        self.rating: float = 0
        self.highest_rating: float = 0

        self.create_table()
        self.client.send_to_server("REQUEST_HIGHSCORE_TABLE",self.username)

        self.client.send_to_server("REQUEST_OWN_HIGHSCORE", self.username)

        self.show_buttons()
        self.start_button = tkinter.Button(self.window, name="start_button", text="Start", command=self.start_game, height=2, width=10).place(x=50, y=400)
        self.time_label = tkinter.Label(self.window, name="start_label", text=f"Time: {self.duration}", height=2, width=10)
        self.time_label.place(x=300, y=400)
        self.exit_button.place(x=550, y=400)

        self.start_loop()


#------------------------MAINLOOP-----------------------#
    def start_loop(self) -> None:
        """
        Starts the loop that updates the Window

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        last_highscore_request = time.time()
        while True:
            if last_highscore_request + 30 <= time.time():
                self.client.send_to_server("REQUEST_HIGHSCORE_TABLE",self.username)
                last_highscore_request = time.time()

            self.handle_server_commands()
            
            self.window.update()


    def handle_server_commands(self) -> None:
        """
        Handle the commands received from the server

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if not self.client.que.empty():
            recv: dict = self.client.que.get()

            match recv.get("command"):
                case "UPDATE_HIGHSCORE_TABLE":
                    self.update_highscore_table(recv)

                case "OWN_HIGHSCORE":
                    self.get_own_highscore(recv)
#------------------------MAINLOOP-----------------------#


#-------------------------LOGIN-------------------------#
    def login_window(self) -> None:
        """
        Changes the Window to the login screen
        Is triggert if client presses on login button in register screen
        Is automatically called when starting the app

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        self.window.geometry("500x400")

        try:
            self.password_confirm_entry.destroy()
            self.password_confirm_label.destroy()
        except AttributeError:
            pass

        self.login_button = tkinter.Button(self.window, name="login_button", text="login", command=self.login, height=2, width=10)
        self.login_button.place(x=10, y=350)

        self.register_button = tkinter.Button(self.window, name="register_button", text="register", command=self.register_window, height=2, width=10)
        self.register_button.place(x=200, y=350)

        self.username_label = tkinter.Label(self.window, name="username_label", text="Username:",height=3,width=10, font=('Arial 15'))
        self.username_label.place(x=10, y=70)

        self.username_entry = tkinter.Entry(self.window, name="username_entry", font=('Arial 15'))
        self.username_entry.place(x=120, y=95)

        self.password_label = tkinter.Label(self.window, name="password_label", text="Password:",height=3,width=10, font=('Arial 15'))
        self.password_label.place(x=10, y=150)

        self.password_entry = tkinter.Entry(self.window, show="*", name="password_entry", font=('Arial 15'))
        self.password_entry.place(x=120, y=175)

        while not self.login_status:
            self.window.update()


    def login(self) -> None:
        """
        Method triggerd by the login button when user is in the login screen
        Calls the setup_connection method and destroys the widgets that are no longer needed

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.setup_connection(register=False)
        
        if self.login_status:
            self.login_button.destroy()
            self.register_button.destroy()
            self.username_entry.destroy()
            self.username_label.destroy()
            self.password_entry.destroy()
            self.password_label.destroy()


    def register_window(self) -> None:
        """
        Changes the Window to the register screen
        Is triggert if client presses on register button in login screen

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.login_button.config(command=self.login_window)
        self.register_button.config(command=self.register)

        self.password_confirm_label = tkinter.Label(self.window, name="confirm_label", text="Confirm:", height=3, width=10, font=('Arial 15'))
        self.password_confirm_label.place(x=10, y=230)

        self.password_confirm_entry = tkinter.Entry(self.window, show="*", name="confirm_entry", font=('Arial 15'))
        self.password_confirm_entry.place(x=120, y=255)


    def register(self) -> None:
        """
        Method triggerd by the register button when user is in the register screen
        Calls the setup_connection method and destroys the widgets that are no longer needed
        The user is loged in automatically

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.setup_connection(register=True)

        if self.login_status:
            self.login_button.destroy()
            self.register_button.destroy()
            self.username_entry.destroy()
            self.username_label.destroy()
            self.password_entry.destroy()
            self.password_label.destroy()
            self.password_confirm_entry.destroy()
            self.password_confirm_label.destroy()


    def setup_connection(self, register: bool) -> None:
        """
        Tries to connect to server and gives pop up if connection to server failed or the login wasn't correct

        Parameters
        ----------
        register : bool
            If register is True the user wants to register if not the user wants to log in into a existing account

        Returns
        -------
        None
        """
        #stores the str the user typed into the username entry field
        self.username = self.username_entry.get()
        if not self.username:
            tkinter.messagebox.showerror("NO USERNAME", message="Please enter a username!")
            return
        if register:
            if not self.password_entry.get():
                tkinter.messagebox.showerror("NO PASSWORD", message="Please enter a password!")
                return
            if self.password_confirm_entry.get() != self.password_entry.get:
                tkinter.messagebox.showerror("PASSWORDS DON'T MATCH", message="Please enter the same password!")
                return


        #checks if there is already a connection
        if not self.client.connected:
            #tries to connect to the server 
            status, reason = self.client.connect_to_server(self.username, self.password_entry.get(), register)

            #if the connection is refused, a error pop up will show
            if isinstance(status, ConnectionRefusedError):
                tkinter.messagebox.showerror("CONNECTION FAILED", message="Couldn't connect to server!")
    
            #if the login credentials were wrong a error pop up will show
            elif status == False:
                tkinter.messagebox.showerror("LOGIN FAILED", message=f"{reason}")
        
            elif status == True:
                self.login_status = True
#-------------------------LOGIN-------------------------#


#-------------------------GAME--------------------------#
    def start_game(self) -> None:
        """
        Starts the game
        Is triggert by the start button in the main window

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        #Checking if there is already a game and starts one if there is not
        if not self.game_running:
            self.reset_stats()
            start_time = time.time()
            self.game_running = True

            #Runs the game as long as the timer is runnning
            while start_time + self.duration >= time.time():
                random_button: GameButton = random.choice(self.buttons)
                random_button.change_color()

                #Updates the screen and waits until the right button is pressed
                while random_button.highlighted == True and start_time + self.duration >= time.time():
                    time_left = str(int(self.duration-(time.time()-start_time)))
                    self.time_label.config(text=f"Time: {time_left}")
                    self.window.update()
                
            self.calculate_stats()
            self.game_running = False
            random_button.reset_button()
            self.show_end_msg()


    def show_end_msg(self) -> None:
        """
        Shows a pop up at the end of the game
        Shows the reached score and if it is a new highscore

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.rating > self.highest_rating:
            self.highscore = self.score
            self.highscore_accuracy = self.accuracy
            self.highest_rating = self.rating

            self.client.send_to_server("NEW_HIGHSCORE", self.username, highscore = self.highscore, \
                                        accuracy = self.highscore_accuracy, time = self.duration)

            tkinter.messagebox.showinfo(title="NEW HIGHSCORE", \
                                                        message=f"Congratulation, you reached a new highscore!\
                                                        \nYour highscore: {self.highscore} with an accuracy of {self.highscore_accuracy}%")
        else:
            tkinter.messagebox.showinfo(title="Game stats", message=f"Your score: {self.score} with an accuracy of {self.accuracy}%\
                                         \nYour highscore: {self.highscore} with an accuracy of {self.highscore_accuracy}%")
#-------------------------GAME--------------------------#


#------------------------OTHER--------------------------#
    def get_own_highscore(self, data: dict) -> None:
        """
        Gets the highscore of the user from the server

        Parameters
        ----------
        data : dict
            The data the client receives

        Returns
        -------
        None
        """
        self.highest_rating = data.get("rating")
        self.highscore = data.get("highscore")
        self.highscore_accuracy = data.get("accuracy")


    def create_table(self) -> None:
        """
        Creats the highscore table

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.highscore_talbe = ttk.Treeview(self.window, column=("c1", "c2", "c3", "c4"), show='headings')

        self.highscore_talbe.column("c1", anchor=tkinter.CENTER, width= 120)
        self.highscore_talbe.heading("c1", text="Name")

        self.highscore_talbe.column("c2", anchor=tkinter.CENTER, width=70)
        self.highscore_talbe.heading("c2", text="Rating")

        self.highscore_talbe.column("c3", anchor=tkinter.CENTER, width=70)
        self.highscore_talbe.heading("c3", text="Score")

        self.highscore_talbe.column("c4", anchor=tkinter.CENTER, width=90)
        self.highscore_talbe.heading("c4", text="Accuracy [%]")
        
        self.highscore_talbe.place(x=330, y=50)


    def update_highscore_table(self, data: dict) -> None:
        """
        Updates the highscore table

        Parameters
        ----------
        data : dict
            The data the client receives

        Returns
        -------
        None
        """
        entries = self.highscore_talbe.get_children()
        for item in entries:
            self.highscore_talbe.delete(item)
        
        rows: list[list[str, int, int]] = data.get("highscores") 
        for row in rows:
            self.highscore_talbe.insert("", tkinter.END, values=row)
        

    def show_buttons(self) -> None:
        """
        Creating the buttons needed for the game
        Showing the buttons on the screen

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.buttons: list[GameButton] = []
        x_pos = [50, 130, 210]
        y_pos = [50, 136, 222]
        for y in y_pos:
            for x in x_pos:
                self.buttons.append(GameButton(self.window, x = x, y = y, text = str(len(self.buttons)+1)))
        

    def calculate_stats(self) -> None:
        """
        Calculates the stats of the last game

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        for button in self.buttons:
            self.score += button.right_pressed
            self.missed_clicks += button.false_pressed
    
        clicks = self.missed_clicks + self.score
        try:
            self.accuracy = round((self.score/clicks) * 100,2)

        except ZeroDivisionError:
            self.accuracy = 0

        self.rating = round((self.score*self.accuracy)/(100*self.duration), 3)
 

    def reset_stats(self) -> None:
        """
        Resets the current game stats

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.score = 0
        self.missed_clicks = 0
        for button in self.buttons:
            button.right_pressed = 0
            button.false_pressed = 0
       

    def exit_app(self) -> None:
        """
        Show pop up if user really want's to exit the app
        Sends the server a command to close the connection
        Closes the window

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if tkinter.messagebox.askyesno(title="EXIT", message="Do you really want to exit the app?"):
            self.client.send_to_server("CLOSE_CONNECTION", self.username)
            self.window.destroy()
            self.client.client_socket.close()
#------------------------OTHER--------------------------#

class GameButton:
    """
    A class to represent and interact with the game button

    ...

    Attributes
    ----------
    button : tkinter.Button
        The button object of tkinter
    highlighted : bool
        The current status of the button
    false_pressed : int
        A counter for the wrong clicks in a game
    right_pressed : int
        A counter for the correct clicks in a game

    Methods
    -------
    change_color() -> None
        Changes the color of the button to read and the highlited status to True
    def check_status() -> None
        Checks if button is highlighted, updates the counters and resets the button if status was True
    reset_button() -> None
        Resets the button to the basic color and sets the highlighted status to Flase
    """
    def __init__(self, window: tkinter.Tk, x: int, y: int, text: str) -> None:
        """
        Initialize a new GameButton

        Parameters
        ----------
        window : tkinter.TK
            The window in which the button should show up
        x : int
            The x-coordinate of the button
        y : int
            The y-coordinate of the button
        text : str
            The text that should be on the button
            
        Returns
        -------
        None
        """
        self.button: tkinter.Button = tkinter.Button(window, text=text, command=self.check_status, height=5, width=10)
        self.button.place(x=x, y=y)
        self.highlighted: bool = False
        self.false_pressed: int = 0
        self.right_pressed: int = 0

    def change_color(self) -> None:
        """
        Changes the color of the button to read and the highlited status to True

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.highlighted = True
        self.button.config(bg="red")

    def check_status(self) -> None:
        """
        Is triggert if the button is clicked
        Checks if button is highlighted
            if its highlighted the counter of the correct presses increases by 1 and resets button
            if its NOT highlighted the counter of the wrong presses increases by 1

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.highlighted == True:
            self.right_pressed += 1
            self.reset_button()
        else: 
            self.false_pressed += 1

    def reset_button(self) -> None:
        """
        Resets the button to the basic color and sets the highlighted status to Flase
        Is called at the end of the game
        Is called if user presses the button and the button is highlighted

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.highlighted = False
        self.button.config(bg="SystemButtonFace")

import tkinter
import tkinter.messagebox
from tkinter import ttk
import random
import time
from client_network import NetworkClient

class App:
    def __init__(self, window: tkinter.Tk, window_title: str) -> None:
        self.client = NetworkClient()

        self.window = window
        self.login_status = False
        self.username: str = ""

        self.exit_button = tkinter.Button(self.window, name="exit_button", text="Exit", command=self.exit_app, height=2, width=10)
        self.exit_button.place(x=400, y=350)

        self.login_window()

        self.window.title(window_title)
        self.window.geometry("700x500")
        self.game_running = False
        self.score = 0
        self.missed_clicks = 0
        self.highscore = 0
        self.accuracy = 100
        self.highscore_accuracy = 0

        self.create_table()
        self.client.send_to_server("REQUEST_HIGHSCORE_TABLE",self.username)

        self.show_buttons()
        self.start_button = tkinter.Button(self.window, name="start_button", text="Start", command=self.start_game, height=2, width=10).place(x=50, y=400)
        self.time_label = tkinter.Label(self.window, name="start_label", text="Time: 5", height=2, width=10)
        self.time_label.place(x=300, y=400)
        self.exit_button.place(x=550, y=400)

        self.start_loop()



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
        while True:
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


    def register(self):
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


    def create_table(self)-> None:
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
        rows: list[list[str, int, int]] = data.get("highscores")
        #TODO: removing old entries in table
        for row in rows:
            self.highscore_talbe.insert("", tkinter.END, values=row)
        


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
            self.client.server.close()


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
                self.buttons.append(GameButton(self.window, x, y, str(len(self.buttons)+1)))
        

    def get_score(self) -> None:
        """
        Iterates through all game buttons and gets the number of the correct and false clicks the user made

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
        duration = 5
        #Checking if there is already a game and starts one if there is not
        if not self.game_running:
            self.reset_stats()
            start_time = time.time()
            self.game_running = True

            #Runs the game as long as the timer is runnning
            while start_time + duration >= time.time():
                random_button: GameButton = random.choice(self.buttons)
                random_button.change_color()

                #Updates the screen and waits until the right button is pressed
                while random_button.highlighted == True and start_time + duration >= time.time():
                    time_left = str(int(duration-(time.time()-start_time)))
                    self.time_label.config(text=f"Time: {time_left}")
                    self.window.update()
                
            self.get_score()
            self.game_running = False
            random_button.reset_button()
            self.show_end_msg()


    def calculate_accuracy(self) -> None:
        """
        Calculates the accuracy of the last game

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        clicks = self.missed_clicks + self.score
        try:
            self.accuracy = round((self.score/clicks) * 100,2)

        except ZeroDivisionError:
            self.accuracy = 0
            

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
        self.calculate_accuracy()
        if self.score > self.highscore:
            self.highscore = self.score
            self.highscore_accuracy = self.accuracy
            tkinter.messagebox.showinfo(title="NEW HIGHSCORE", \
                                                        message=f"Congratulation, you reached a new highscore!\
                                                        \nYour highscore: {self.highscore} with an accuracy of {self.highscore_accuracy}%")
        else:
            tkinter.messagebox.showinfo(title="Game stats", message=f"Your score: {self.score} with an accuracy of {self.accuracy}%\
                                         \nYour highscore: {self.highscore} with an accuracy of {self.highscore_accuracy}%")



class GameButton:
    def __init__(self, window: tkinter.Tk, x: int, y: int, text: str) -> None:
        self.button = tkinter.Button(window, text=text, command=self.check_status, height=5, width=10)
        self.button.place(x=x, y=y)
        self.highlighted = False
        self.false_pressed = 0
        self.right_pressed = 0

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
            if its highlighted the counter of the correct presses increases by 1
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

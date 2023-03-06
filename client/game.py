import tkinter
import tkinter.messagebox
import random
import time

class App:
    def __init__(self, window: tkinter.Tk, window_title: str) -> None:
        self.window = window
        self.login_status = False

        self.login_window()

        self.window.title(window_title)
        self.window.geometry("700x500")
        self.game_running = False
        self.score = 0
        self.missed_clicks = 0
        self.high_score = 0
        self.accuracy = 100
        self.high_score_accuracy = 0

        self.show_buttons()
        self.start_button = tkinter.Button(self.window, text="Start", command=self.start_game, height=2, width=10).place(x=50, y=400)
        self.exit_button = tkinter.Button(self.window, text="Exit", command=self.exit_app, height=2, width=10).place(x=550, y=400)
        self.time_label = tkinter.Label(self.window, text="Time: 5", height=2, width=10)
        self.time_label.place(x=300, y=400)

        self.window.mainloop()

    def login_window(self) -> None:
        self.window.geometry("500x300")
        self.login_button = tkinter.Button(self.window, text="login", command=self.login, height=2, width=10)
        self.login_button.place(x=10, y=250)

        self.register_button = tkinter.Button(self.window, text="register", command=self.register, height=2, width=10)
        self.register_button.place(x=400, y=250)

        self.user_name_label = tkinter.Label(self.window,text="Username:",height=3,width=10, font=('Arial 15'))
        self.user_name_label.place(x=10, y=70)

        self.user_name_entry = tkinter.Entry(self.window, font=('Arial 15'))
        self.user_name_entry.place(x=120, y=95)

        self.password_label = tkinter.Label(self.window,text="Password:",height=3,width=10, font=('Arial 15'))
        self.password_label.place(x=10, y=150)

        self.password_entry = tkinter.Entry(self.window, font=('Arial 15'))
        self.password_entry.place(x=120, y=175)

        while not self.login_status:
            self.window.update()


    def register_window(self) -> None:
        pass

    def login(self):
        self.login_status = True

        self.login_button.destroy()
        self.register_button.destroy()
        self.user_name_entry.destroy()
        self.user_name_label.destroy()
        self.password_entry.destroy()
        self.password_label.destroy()

    def register(self):
        pass



    def exit_app(self) -> None:
        if tkinter.messagebox.askyesno(title="EXIT", message="Do you really want to exit the app?"):
            self.window.quit()


    def show_buttons(self) -> None:
        self.buttons: list[GameButton] = []
        x_pos = [50, 130, 210]
        y_pos = [50, 136, 222]
        for y in y_pos:
            for x in x_pos:
                self.buttons.append(GameButton(self.window, x, y, str(len(self.buttons)+1)))
        

    def get_score(self) -> None:
        for button in self.buttons:
            self.score += button.right_pressed
            self.missed_clicks += button.false_pressed
    

    def reset_stats(self) -> None:
        self.score = 0
        self.missed_clicks = 0
        for button in self.buttons:
            button.right_pressed = 0
            button.false_pressed = 0


    def start_game(self) -> None:
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
        clicks = self.missed_clicks + self.score
        try:
            self.accuracy = round((self.score/clicks) * 100,2)

        except ZeroDivisionError:
            self.accuracy = 0
            

    def show_end_msg(self) -> None:
        self.calculate_accuracy()
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_accuracy = self.accuracy
            tkinter.messagebox.showinfo(title="NEW HIGHSCORE", \
                                                        message=f"Congratulation, you reached a new highscore!\
                                                        \nYour highscore: {self.high_score} with an accuracy of {self.high_score_accuracy}%")
        else:
            tkinter.messagebox.showinfo(title="Game stats", message=f"Your score: {self.score} with an accuracy of {self.accuracy}%\
                                         \nYour highscore: {self.high_score} with an accuracy of {self.high_score_accuracy}%")



class GameButton:
    def __init__(self, window: tkinter.Tk, x: int, y: int, text: str) -> None:
        self.button = tkinter.Button(window, text=text, command=self.check_status, height=5, width=10)
        self.button.place(x=x, y=y)
        self.highlighted = False
        self.false_pressed = 0
        self.right_pressed = 0

    def change_color(self) -> None:
        self.highlighted = True
        self.button.config(bg="red")

    def check_status(self) -> None:
        if self.highlighted == True:
            self.right_pressed += 1
            self.highlighted = False
            self.button.config(bg="SystemButtonFace")
        else: 
            self.false_pressed += 1

    def reset_button(self) -> None:
        self.highlighted = False
        self.button.config(bg="SystemButtonFace")

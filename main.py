import tkinter
import random
import time

class App:
    def __init__(self, window: tkinter.Tk, window_title: str) -> None:
        self.window = window
        self.window.title(window_title)
        self.window.geometry("700x500")
        self.game_running = False
        self.score = 0

        self.show_buttons()
        self.start_button = tkinter.Button(self.window, text="Start", command=self.start_game, height=2, width=10).place(x=50, y=400)
        self.time_label = tkinter.Label(self.window, text="Time: 30", height=2, width=10).place(x=300, y=400)

        self.window.mainloop()
 

    def show_buttons(self) -> None:
        self.buttons = []
        x_pos = [50, 130, 210]
        y_pos = [50, 136, 222]
        for y in y_pos:
            for x in x_pos:
                self.buttons.append(GameButton(self.window, x, y, str(len(self.buttons)+1)))
        
    
    def start_game(self) -> None:
        if not self.game_running:
            start_time = time.time()
            while start_time + 30 >= time.time():
                self.game_running = True
                random_button: GameButton = random.choice(self.buttons)
                random_button.change_color()
                while random_button.highlighted == True:
                    self.window.update()




class GameButton:
    def __init__(self, window: tkinter.Tk, x: int, y: int, text: str) -> None:
        self.button = tkinter.Button(window, text=text, command=self.check_status, height=5, width=10)
        self.button.place(x=x, y=y)
        self.highlighted = False

    def change_color(self) -> None:
        self.highlighted = True
        self.button.config(bg="red")

    def check_status(self) -> None:
        if self.highlighted == True:
            self.highlighted = False
            self.button.config(bg="SystemButtonFace")



if __name__ == '__main__':
    App(tkinter.Tk(), "Useless GUI")
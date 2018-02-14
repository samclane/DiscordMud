from tkinter import *

class Window(Frame):

    def __init__(self, master=None, gameSettings=None):
        Frame.__init__(self, master)
        self.master = master
        self.gameSettings = gameSettings
        self.init_window()

    def init_window(self):
        self.master.title("DiscordMUD")
        self.pack(fill=BOTH, expand=1)
        MapCanvas = Canvas(self, width=1450, height=1450)
        MapCanvas.pack()
        Map = self.gameSettings['world'].Map
        MapScale = 10
        for row in Map:
            for square in row:
                x1, y1 = MapCanvas.canvasx(MapScale*(square.X)), MapCanvas.canvasy(MapScale*(square.Y))
                x2, y2 = MapCanvas.canvasx(MapScale*(square.X + 1)), MapCanvas.canvasy(MapScale*(square.Y + 1))
                MapCanvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff")


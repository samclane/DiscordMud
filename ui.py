from tkinter import *
import os
import gamespace

class Window(Frame):
    REFRESH_RATE = 2000
    img_dict = {}

    def __init__(self, master=None, gameWorld=None):
        Frame.__init__(self, master)
        self.master = master  # same as 'root' in tk-speak
        self.gameWorld = gameWorld
        self.init_window()

    def init_window(self):
        self.master.title("DiscordMUD")
        self.pack(fill=BOTH, expand=1)
        self.MapCanvas = Canvas(self, width=1450, height=1450)
        self.MapCanvas.pack(expand=YES, fill=BOTH)
        Map = self.gameWorld.Map
        MapScale = 20
        self.master.grass = grass = PhotoImage(file=r'res/grass.gif')
        self.master.town = town = PhotoImage(file=r'res/town.gif')
        self.master.wild = wild = PhotoImage(file=r'res/wild.gif')
        for row in Map:
            for square in row:
                y1, x1 = MapScale * square.X, MapScale * square.Y
                y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
                if type(square) is gamespace.Space:
                    self.MapCanvas.create_image(x1, y1, image=grass, anchor=NW)
                    self.img_dict[square] = grass
                elif type(square) is gamespace.Wilds:
                    self.MapCanvas.create_image(x1, y1, image=wild, anchor=NW)
                    self.img_dict[square] = wild
                elif type(square) is gamespace.Town:
                    self.MapCanvas.create_image(x1, y1, image=town, anchor=NW)
                    self.img_dict[square] = town
        Users = self.gameWorld.Users
        for user in Users.values():
            square = user.Location
            y1, x1 = MapScale * square.X, MapScale * square.Y
            y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
            self.MapCanvas.create_rectangle(x1, y1, x2, y2, fill='#000000')
            
    def update(self):
        self.master.player = player = PhotoImage(file=r'res/player.gif')
        MapScale = 20
        Users = self.gameWorld.Users
        for user in Users.values():
            square = user.Location
            y1, x1 = MapScale * square.X, MapScale * square.Y
            y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
            # self.MapCanvas.create_rectangle(x1, y1, x2, y2, fill='#000000')
            self.MapCanvas.create_image(x1, y1, image=player, anchor=NW)
        self.master.after(self.REFRESH_RATE, self.update)

    def on_closing(self):
        self.master.destroy()
        os._exit(1)  # Dirty way to close all threads and end the program

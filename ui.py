import os
from tkinter import *

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
                # y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
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
        # create a toplevel menu
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New World...", command=self.new_world)
        filemenu.add_command(label="Add Town", command=self.add_town)
        filemenu.add_command(label="Add Wilds", command=self.add_wilds)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label="Quit", command=self.on_closing)
        # display the menu
        self.master.config(menu=menubar)

    def update(self):
        self.master.player = player = PhotoImage(file=r'res/player.gif')
        MapScale = 20
        Users = self.gameWorld.Users
        for user in Users.values():
            square = user.Location
            y1, x1 = MapScale * square.X, MapScale * square.Y
            # y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
            # self.MapCanvas.create_rectangle(x1, y1, x2, y2, fill='#000000')
            self.MapCanvas.create_image(x1, y1, image=player, anchor=NW)
        for town in self.gameWorld.Towns:
            y1, x1 = MapScale * town.X, MapScale * town.Y
            self.MapCanvas.create_image(x1, y1, image=self.master.town, anchor=NW)
        for wild in self.gameWorld.Wilds:
            y1, x1 = MapScale * wild.X, MapScale * wild.Y
            self.MapCanvas.create_image(x1, y1, image=self.master.wild, anchor=NW)
        self.master.after(self.REFRESH_RATE, self.update)

    def new_world(self):
        d = NewWorldDialog(self.master)
        print(d.result)

    def add_wilds(self):
        pass

    def add_town(self):
        pass

    def on_closing(self):
        self.master.destroy()
        os._exit(1)  # Dirty way to close all threads and end the program


# boilerplate code from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
class Dialog(Toplevel):

    def __init__(self, parent, title=None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1  # override

    def apply(self):
        pass  # override


class NewWorldDialog(Dialog):
    result = None

    def body(self, master):
        Label(master, text="xWidth:").grid(row=0)
        Label(master, text="yHeight:").grid(row=1)

        self.xWidth = Entry(master)
        self.yHeight = Entry(master)

        self.xWidth.grid(row=0, column=1)
        self.yHeight.grid(row=1, column=1)
        return self.xWidth  # initial focus

    def apply(self):
        first = int(self.xWidth.get())
        second = int(self.yHeight.get())
        self.result = first, second

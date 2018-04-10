import os
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import gamespace


class Window(Frame):
    REFRESH_RATE = 2000
    img_dict = {}

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master  # same as 'root' in tk-speak
        self.gameWorld = None
        self.init_window()

    def init_window(self):
        self.master.title("DiscordMUD")
        self.pack(fill=BOTH, expand=1)
        self.MapCanvas = Canvas(self, width=1450, height=1450)
        self.MapCanvas.pack(expand=YES, fill=BOTH)
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

    def init_map(self):
        if self.gameWorld is None:
            print("Tried to init a null world. Ignoring.")
            return
        self.MapCanvas.delete("all")
        Map = self.gameWorld.Map
        MapScale = 20
        self.master.grass = grass = PhotoImage(file=r'res/grass.gif')
        self.master.town = town = PhotoImage(file=r'res/town.gif')
        self.master.wild = wild = PhotoImage(file=r'res/wild.gif')
        self.master.player = player = PhotoImage(file=r'res/player.gif')
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

    def update(self):
        if self.gameWorld is None:
            self.master.after(self.REFRESH_RATE, self.update)
            return
        MapScale = 20
        Users = self.gameWorld.Users
        for user in Users.values():
            square = user.Location
            y1, x1 = MapScale * square.X, MapScale * square.Y
            # y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
            # self.MapCanvas.create_rectangle(x1, y1, x2, y2, fill='#000000')
            self.MapCanvas.create_image(x1, y1, image=self.master.player, anchor=NW)
        for town in self.gameWorld.Towns:
            y1, x1 = MapScale * town.X, MapScale * town.Y
            self.MapCanvas.create_image(x1, y1, image=self.master.town, anchor=NW)
        for wild in self.gameWorld.Wilds:
            y1, x1 = MapScale * wild.X, MapScale * wild.Y
            self.MapCanvas.create_image(x1, y1, image=self.master.wild, anchor=NW)
        for user in Users.values():
            square = user.Location
            y1, x1 = MapScale * square.X, MapScale * square.Y
            # y2, x2 = MapScale * (square.X + 1), MapScale * (square.Y + 1)
            # self.MapCanvas.create_rectangle(x1, y1, x2, y2, fill='#000000')
            self.MapCanvas.create_image(x1, y1, image=self.master.player, anchor=NW)
        self.master.after(self.REFRESH_RATE, self.update)

    def new_world(self):
        if self.gameWorld is not None:
            result = messagebox.showwarning("World already exists",
                                            "Are you sure you want to delete the existing world?",
                                            type=messagebox.YESNO)
            if result == 'no':
                return
        d = NewWorldDialog(self.master)
        self.gameWorld = d.result
        self.init_map()

    def add_wilds(self):
        if self.gameWorld is None:
            messagebox.showerror("No world", "Please make a world in order to add a wilds.")
            return
        d = NewWildsDialog(self.master)
        self.gameWorld.addWilds(d.result)

    def add_town(self):
        if self.gameWorld is None:
            messagebox.showerror("No world", "Please make a world in order to add a town.")
            return
        d = NewTownDialog(self.master)
        self.gameWorld.addTown(d.result, d.IsStartingTown)

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
    X_MAX = Y_MAX = 50

    def body(self, master):
        Label(master, text="xWidth:").grid(row=0)
        Label(master, text="yHeight:").grid(row=1)

        self.xWidth = Entry(master)
        self.yHeight = Entry(master)

        self.xWidth.grid(row=0, column=1)
        self.yHeight.grid(row=1, column=1)
        return self.xWidth  # initial focus

    def validate(self):
        x = int(self.xWidth.get())
        y = int(self.yHeight.get())
        if x > self.X_MAX or y > self.Y_MAX:
            messagebox.showerror("World too large!",
                                 "X must be < {} and Y must be < {}".format(self.X_MAX, self.Y_MAX))
            return 0
        else:
            self.result = gamespace.World(x, y)
            return 1


class NewTownDialog(Dialog):
    result = None
    IsStartingTown = False

    def body(self, master):
        Label(master, text="xCoord:").grid(row=0)
        Label(master, text="yCoord:").grid(row=1)
        Label(master, text="Name:").grid(row=2)
        Label(master, text="Population:").grid(row=3)
        Label(master, text="Industry:").grid(row=4)
        # Label(master, text="Starting Town?:").grid(row=5)

        self.x = Entry(master)
        self.y = Entry(master)
        self.Name = Entry(master)
        self.Population = Entry(master)
        self.Industry = ttk.Combobox(master)
        self.Industry['values'] = list(gamespace.IndustryType)
        self.st = IntVar()
        self.StartingTownButton = Checkbutton(master, text="Starting Town?:",
                                              variable=self.st)  # self.st is hacky way to store button value until validation

        self.x.grid(row=0, column=1)
        self.y.grid(row=1, column=1)
        self.Name.grid(row=2, column=1)
        self.Population.grid(row=3, column=1)
        self.Industry.grid(row=4, column=1)
        self.StartingTownButton.grid(row=5)

        return self.x

    def validate(self):
        x = int(self.x.get())
        y = int(self.y.get())
        name = str(self.Name.get())
        pop = int(self.Population.get())
        industry = eval("gamespace." + self.Industry.get())  # TODO: Find a way to make this not use eval
        self.IsStartingTown = bool(self.st.get())

        # TODO validate this stuff
        self.result = gamespace.Town(x, y, name, pop, industry)
        return 1

class NewWildsDialog(Dialog):
    result = None

    def body(self, master):
        Label(master, text="xWidth:").grid(row=0)
        Label(master, text="yHeight:").grid(row=1)
        Label(master, text="Name:").grid(row=2)

        self.x = Entry(master)
        self.y = Entry(master)
        self.Name = Entry(master)

        self.x.grid(row=0, column=1)
        self.y.grid(row=1, column=1)
        self.Name.grid(row=2, column=1)
        return self.x  # initial focus

    def validate(self):
        x = int(self.x.get())
        y = int(self.y.get())
        name = str(self.Name.get())

        # TODO Validate this stuff
        self.result = gamespace.Wilds(x, y, name)
        return 1
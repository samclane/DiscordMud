import sys
import threading
import time

from PyQt5.QtWidgets import QApplication

from gamelogic import events, gamespace
from gui import ui

world = None
app = None

game_channel = None  # The public text channel where public events take place


# my test routine to initialize the world. Should be replaced with ui stuff eventually
def default_init(xWidth, yHeight):
    world = gamespace.World(xWidth, yHeight)
    example_town = gamespace.Town(5, 3, 'Braxton', 53, gamespace.MiningIndustry)
    world.addTown(example_town, True)
    example_wilds = gamespace.Wilds(5, 2, 'The Ruined Forest')
    event1 = events.CombatEvent(.5, "Test monster appears", "TODO: Monster class", "TODO: conditions class")
    example_wilds.addEvent(event1)
    event2 = events.EncounterEvent(.5, "You found a friendly scav", {"Give meds": "Get $100", "Kill him": "Get pistol"},
                                   "TODO: NPC class")
    example_wilds.addEvent(event2)
    world.addWilds(example_wilds)
    world.StartingTown = example_town
    return world


def listenForWorld():
    global world
    while True:
        world = app.gameWorld
        time.sleep(.25)


# This is required to get PyQt to print runtime exceptions
def excepthook(cls, exception, traceback):
    raise Exception("{}".format(exception))


if __name__ == "__main__":
    import discord_interface.player_interface as player_interface
    import discord_interface.basic_bot as gBot

    sys.excepthook = excepthook

    app = QApplication(sys.argv)
    threads = {}
    # initialize the bot
    W = H = 50
    world = default_init(W, H)
    pi = player_interface.setup(gBot.bot, world)
    pi.registered.connect(world.addActor)
    tBot = threading.Thread(target=gBot.bot.run, args=(gBot.TOKEN,), daemon=True)
    threads['bot'] = tBot
    tBot.start()
    main_window = ui.MainWindow(app, world)
    pi.registered.connect(main_window.update)
    pi.moved.connect(main_window.update)
    sys.exit(app.exec_())

    """
    # initialize the bot
    # world = default_init(50, 50)
    tBot = threading.Thread(target=bot.run, args=(token,))
    threads['bot'] = tBot
    tBot.start()

    # initialize the gui
    root = ui.Tk()
    root.geometry("500x500")
    app = ui.Window(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # close all threads on exit
    root.after(app.REFRESH_RATE, app.update)  # set update hook

    # my hacky way of updating the world
    worldListener = threading.Thread(target=listenForWorld)
    threads['worldlistener'] = worldListener
    worldListener.start()

    # start GUI (LEAVE THIS LAST)
    # apparently can't run tk in a non-main thread
    root.mainloop()
    """

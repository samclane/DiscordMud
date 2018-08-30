import os
import pickle
import sys
import threading

from PyQt5.QtWidgets import QApplication

from gamelogic import events, gamespace
from gui import ui
from gui.dialogs import AddWorldDialog

world: gamespace.World = None
app = None

game_channel = None  # The public text channel where public events take place


# my test routine to initialize the world. Should be replaced with ui stuff eventually
def default_init(xWidth, yHeight):
    world = gamespace.World("Testworld", xWidth, yHeight)
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


if __name__ == "__main__":
    import discord_interface.player_interface as player_interface
    import discord_interface.basic_bot as gBot

    sys._excepthook = sys.excepthook


    # This is required to get PyQt to print runtime exceptions
    def excepthook(cls, exception, traceback):
        print(cls, exception, traceback)
        sys._excepthook(cls, exception, traceback)
        sys.exit(1)


    sys.excepthook = excepthook

    app = QApplication(sys.argv)
    threads = {}

    # Have world be built by user.
    if os.path.isfile(r'./world.p'):
        world = pickle.load(open(r"./world.p", "rb"))
    else:
        dialog = AddWorldDialog()
        if dialog.exec_():
            world = dialog.returnData
        else:
            sys.exit(-1)

    # Start player interface bot in separate thread
    pi = player_interface.setup(gBot.bot, world)
    pi.registered.connect(world.addActor)
    tBot = threading.Thread(target=gBot.bot.run, args=(gBot.TOKEN,), daemon=True)
    threads['bot'] = tBot
    tBot.start()

    # Start main Qt window
    main_window = ui.MainWindow(app, world)
    pi.registered.connect(main_window.update)
    pi.registered.connect(lambda pc: main_window.logger.info(pc.Name + " has joined the world."))
    pi.moved.connect(main_window.update)
    pi.moved.connect(lambda pc: main_window.logger.info("{} has moved to {}".format(pc.Name, pc.Location)))
    pi.requestScreenshot.connect(
        lambda pc: main_window.worldFrame.saveSubimage(world.getAdjacentSpaces(pc.Location, pc.FOV_Default),
                                                       "capture-{}.png".format(pc.Name)))

    # Begin application, and exit when it returns
    sys.exit(app.exec_())

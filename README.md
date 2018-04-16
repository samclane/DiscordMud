# DiscordMud
MUD game and server that uses discord as a player interface

# Installation
Requires `discord.py`.

In order to run, you must set up and configure your own user bot. More info can be found [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token). 

Once you get a token, create a new environmental variable called `DISCORD_BOT_TOKEN`, and set it to be your token. 

Then, run `main.py`. Your bot should log in, and a tk GUI should appear. 

![main window](https://i.imgur.com/SfU71WF.png)

# Getting started
Go to `File` -> `New World...` and enter the worlds size. When you are done, some grass should appear. 

![grass window](https://i.imgur.com/bbO7O1C.png)

Once your world is created, you need to add a starting town, Go to `File` -> `Add Town`, and fill in the town's info. Be sure to check `Starting Town` checkbox, as this will give your players a place to spawn.

![town window](https://i.imgur.com/cFKHNSA.png)

Now it is time to create a character. The prefix for the bot is `*` by default. In a valid chat channel, type `*register`. The bot will ask you if you want to join the server. Type `yes`. The bot will then prompt you to name your character. Once you have given your character a name, you should see it spawn on top of the starting town in the GUI. 

![character window](https://i.imgur.com/uvesmNP.png)

You can now move your character around by entering `*go`, then `n`, `e`, `s`, `w`, into chat. 

In order to see an image of the world, type `*world`. You don't even need to be registered. The bot should DM you a picture shortly. 

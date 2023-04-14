
## PickupLeagueRemaster description
New python based version of a similar concept to the pickup league bot

## Discord py library docs
https://discordpy.readthedocs.io/en/stable/

# For running the bot locally
## Prerequisites

Installed python interpreter
Installed discord.py library https://pypi.org/project/discord.py/

## Setting up a bot
1. Log into discord here:
https://discord.com/developers/applications

2. Create a new application
3. Name your new bot
4. Select your newly created bot
5. Settings > Bot > give your new bot life. In privileged Gateway Intents for now we only need Message Content. (subject to change)
6. In OAuth2 you'll find your client secret. Add this to your clone of the secrets.json file found in this repo.
7. Use the URL Generator found under OAuth2, for now we only need bot and applications.commands selected (subject to change)
8. For a test bot we can just give it administrator rights, with the real thing we can select the permissions it actually needs.
9. Copy/paste the generated URL into your browser to be brought to a menu where you can choose what server to add the bot to.
10. Run main.py to turn the bot on.
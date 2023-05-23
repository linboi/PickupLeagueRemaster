
# PickupLeagueRemaster

Pickup league bot for League of Legends using [discord.py](https://discordpy.readthedocs.io/en/stable/)

## Features

- Internal MMR system
- Matchmaking
- Leaderboard

## Running Locally

### Prerequisites

- Python  
- SQLITE3 Database

### Setting up a bot

1. Create a developer application on discord:
   1. Log in to the discord [developer applications page](https://discord.com/developers/applications)
   2. Create a new application
   3. Name your new bot
   4. Select your newly created bot
   5. Settings > Bot > give your new bot life. In `Privileged Gateway Intents`, we only need `Message Content` (subject to change)
   6. In `OAuth2` you'll find your client secret
   7. Use the URL Generator found under OAuth2, for now we only need `bot` and `applications.commands` selected (subject to change)
   8. Test bots can just be given administrator rights. (Permissions list **WIP**)
   9. Add permissions for all three toggles (as you will need member access)
   10. Copy/paste the generated URL into your browser to be brought to a menu where you can choose what server to add the bot to.
2. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) this repo
3. Fill in your `.env` file with bot secrets and discord-server specific details (Example .env file **WIP**)
4. [Activate the virtual environment](https://realpython.com/python-virtual-environments-a-primer/#activate-it) (Optional but prevents requirement versioning collisions with other python projects)
5. Install the requirements via `pip install -r requirements.txt`
6. Run `main.py` to turn the bot on

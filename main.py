import discord
import json
import sqlite3
import os
from dotenv import load_dotenv
from commands import commands
from serverInstance import serverInstance

# Load Environment variables
load_dotenv()

# Setup connection to database
con = sqlite3.connect(os.getenv('DATABASE'))
cursor = con.cursor()
print("Connected to SQL Database ✨")

# Define Intents
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
inst = serverInstance()

# DEFINE Channel Names
main_channel_id = os.getenv('MAIN_CHANNEL')
role_channel_id = os.getenv('ROLE_CHANNEL')
game_channel_id = os.getenv('GAME_CHANNEL')
announcement_channel_id = os.getenv('ANNOUNCEMENT_CHANNEL')
general_channel_id = os.getenv('GENERAL_CHANNEL')
watched_channels = os.getenv('WATCHED_CHANNELS').split(" ")
voice_channels = os.getenv("VOICE_CHANNELS").split(" ")

# ROLE ID
puRoleID = os.getenv("ROLE_ID")

# DEFINE Messages
primary_role_msg = os.getenv('PRIMARY_ROLE_MSG')
secondary_role_msg = os.getenv('SECONDARY_ROLE_MSG')


@client.event
# Connection to Client is established
async def on_ready():
    # Get Channel() from ID
    main_channel = client.get_channel(int(main_channel_id))
    role_channel = client.get_channel(int(role_channel_id))
    announcement_channel = client.get_channel(int(announcement_channel_id))
    general_channel = client.get_channel(int(general_channel_id))
    game_channel = client.get_channel(int(game_channel_id))
    role_id = int(puRoleID)

    inst.ready(client, role_channel, main_channel, announcement_channel, general_channel,
               game_channel, voice_channels, role_id, primary_role_msg, secondary_role_msg, cursor, con)

    with open('./settings.json') as f:
        settings = json.load(f)

    await inst.createGamesOnSchedule(settings['GameDays'], announcement_channel)


@client.event
# Event handler for Messages
async def on_message(message):
    if str(message.channel.id) in os.getenv('WATCHED_CHANNELS'):
        await commands.parse(message, inst)


@client.event
# Event handler for Reactions
async def on_raw_reaction_add(reaction):
    await commands.parseReaction(reaction, inst)


def main():
    client.run(os.getenv('BOT_TOKEN'))


if __name__ == '__main__':
    main()

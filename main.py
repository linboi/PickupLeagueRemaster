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
intents.members= True

client = discord.Client(intents=intents)
inst = serverInstance()

# Connection to Client is established
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
    # Create Global Variables for #select-role, and #testing channels
    for guild in client.guilds:
        for channel in guild.text_channels:
            if str(channel).strip() == "select-role":
                # #select-role text channel
                global select_role_channel
                select_role_channel = channel
                
            if str(channel).strip() == "testing":
                # #testing channel
                global main_channel
                main_channel = channel
    
    inst.ready(client, 1098221994555740190, select_role_channel, main_channel, cursor, con)
                 
# Event handeler for Messages
@client.event
async def on_message(message):
    await commands.parse(message, inst)
        
# Event handeler for Reactions
@client.event
async def on_raw_reaction_add(reaction):
    await commands.parseReaction(reaction, inst)
     
def main():	
	with open('./settings.json') as f:
	
		settings = json.load(f)
		
	client.run(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
	main()
import discord
import json
import sqlite3
import urllib3
import os
from dotenv import load_dotenv
from commands import commands
from serverInstance import serverInstance

# Setup connection to database
con = sqlite3.connect('irishl.db')
cursor = con.cursor()
print("Connected to SQL Database ✨")

# Load Environment variables
load_dotenv()

# Load Environment variables
load_dotenv()

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
	inst.ready(client, 1098221994555740190)
	# Create Global Variables for #select-role, and #testing channels
	for guild in client.guilds:
		for channel in guild.text_channels:
			if str(channel).strip() == "select-role":
				global channel_id
				channel_id = channel.id

			if str(channel).strip() == "testing":
				global main_channel
				main_channel = channel
		
		
# Event handeler
@client.event
async def on_message(message):
	 await commands.parse(message, inst)
   
# Select Role based on Reaction 
@client.event
async def on_raw_reaction_add(reaction):
	if reaction.channel_id == channel_id and str(reaction.message_id) == '1098222182997442611':
		# Jungle Selected
		if str(reaction.emoji) == "✨"  :
			print("Set Role as Jungle")  
			user_name = await client.fetch_user(reaction.user_id)
			await main_channel.send(f"✨ {user_name} has changed their primary role to JG") 
		# Mid Selected
		elif str(reaction.emoji) == "😎"  :
			print("Set Role as Mid")  
			user_name = await client.fetch_user(reaction.user_id)
			await main_channel.send(f"✨ {user_name} has changed their primary role to MID")
		# Top Selected
		elif str(reaction.emoji) == "🥶"  :
			print("Set Role as TOP")  
			user_name = await client.fetch_user(reaction.user_id)
			await main_channel.send(f"✨ {user_name} has changed their primary role to TOP")
		# AD Selected
		elif str(reaction.emoji) == "😭"  :
			print("Set Role as AD")  
			user_name = await client.fetch_user(reaction.user_id)
			await main_channel.send(f"✨ {user_name} has changed their primary role to AD")
		# Support Selected
		elif str(reaction.emoji) == "🤡"  :
			print("Set Role as SUP")  
			user_name = await client.fetch_user(reaction.user_id)
			await main_channel.send(f"✨ {user_name} has changed their primary role to SUP")	 
		


def main():	
	with open('./settings.json') as f:
	
		settings = json.load(f)
		
	client.run(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
	main()
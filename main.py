import discord
import json
import sqlite3
import requests
import urllib3
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Setup connection to database
con = sqlite3.connect('irishl.db')
cursor = con.cursor()
print("Connected")

# Load Environment variables
load_dotenv()

# Define Intents
intents = discord.Intents.all()
intents.message_content = True
intents.members= True

client = discord.Client(intents=intents)

# Connection to Client is established
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
    # Create Global Variables for #select-role, and #testing channels
    for guild in client.guilds:
        for channel in guild.text_channels:
            if str(channel).strip() == "select-role":
                global channel_id
                channel_id = channel.id
                print("✨")
            if str(channel).strip() == "testing":
                global main_channel
                main_channel = channel
                print(str(main_channel))
    
    async for member in guild.fetch_members(limit=150):
        print(member.name)
    
    
# Event handeler
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Fionn is a dog 🐶!')
        
    if message.content.startswith('$fetch'):
        await message.channel.send('Exit')
    
    # Signup command
    if(message.content.startswith('!signup')):
        # Remove command from msg
        msg_content = message.content
        msg_content = msg_content.replace("!signup", "")
        # Scrape op.gg link
        pRank, pName = await opggWebScrape(msg_content, message.author)
        # Give access to '#select-roles' channel
        await message.channel.send(pName + " (" + pRank + ")" + "\n" + str(message.author.id))
   
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
        
    
# Scrape rank details from op.gg page
async def opggWebScrape(msg_content, discord_id):
    
    # Assign Headers, so scraping is not BLOCKED
    headers = requests.utils.default_headers()
    headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })
    
    # Try scrape OP.GG URL
    try:
        op_url = msg_content
        res_url = requests.get(op_url, headers=headers)
        doc = BeautifulSoup(res_url.text, "html.parser")
    except:
        summoner_name = "Invalid Account"
        rank_str = "Invalid Link"
        
    # Try scraping valid OP.GG URL - Rank, Summoner Name.
    try:
        rank = doc.find_all(class_="tier")
        rank = rank[0].decode_contents().strip()
        rank = rank.replace("<!-- -->", "")
        rank = rank.split()
        rank_str = ""
        for char in rank:
            rank_str += char[0]
                
        summoner_name = doc.find_all(class_="summoner-name")
        summoner_name = summoner_name[0].decode_contents().strip()
        
        # Insert into DB - discord ID✅, Name✅, Rank✅
        # Give access to #select-role text channel
       
    except:
        rank_str = "Invalid Account"
        summoner_name = "Invalid Account"
    
    
    return rank_str.upper(), summoner_name

def main():	
	with open('./settings.json') as f:
	
		settings = json.load(f)
    
	client.run(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
	main()
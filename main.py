import discord
import json
import sqlite3
import requests
import urllib3
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Setup connection to database
con = sqlite3.connect('copy.db')
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
                
    
    
# Event handeler
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Fionn is a dog 🐶!')
        
    if message.content.startswith('$add'):
        # Test function to add player to db, and check if that players exists already
        
        # Discord id
        discordID = message.author.id
        
        # Check if the discordID already exists in DB
        res = cursor.execute(f"SELECT COUNT(*) FROM Player WHERE discordID = '{discordID}'")
        result = res.fetchone()
        
        if result[0] > 0:
            await message.channel.send('😭 Player exists in the table, unable to register again!')
        else:
            await message.channel.send('😁 Player does not exist in the table')
            await message.channel.send('🥰 Adding to table..')
            cursor.execute(f"INSERT INTO Player (discordID, winCount, lossCount, internalRating) VALUES ({discordID}, 0, 0, 1500)")
            con.commit()
            # Add player account to Account table
    
    # Signup command
    if(message.content.startswith('!signup')):
        # Remove command from msg
        msg_content = message.content
        msg_content = msg_content.replace("!signup", "")
        # Scrape op.gg link
        pRank, pName, signUpSuccess = await opggWebScrape(msg_content, message)
        # Give access to '#select-roles' channel
        if(signUpSuccess):
            await message.channel.send(pName + " (" + pRank + ")" + "\n" + str(message.author.id))
            await message.channel.send(f"Succes 😁 head over to {select_role_channel.mention} to assign your primary and secondary role!")
        else:
            await message.channel.send(pName + " (" + pRank + ")" + "\n" + str(message.author.id))
            await message.channel.send("Failed 😔 please try again!")
        
   
# Select Role based on Reaction 
@client.event
async def on_raw_reaction_add(reaction):
    if reaction.channel_id == select_role_channel.id and str(reaction.message_id) == '1098222182997442611':
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
async def opggWebScrape(msg_content, message_obj):
    
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
        success = False
        
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
        
        
        # Give access to #select-role text channel (change permissions)
        for guild in client.guilds:
            for member in guild.members:
                if (member.id == message_obj.author.id):
                    overwrite = discord.PermissionOverwrite()
                    overwrite.send_messages = False
                    overwrite.read_messages = True
                    await select_role_channel.set_permissions(member, overwrite=overwrite)
                    print(f"Access granted to #select-role 🙌 for {member.name}")
        
        
        success = True
        
       
    except:
        rank_str = "Invalid Account"
        summoner_name = "Invalid Account"
        success = False
    
    
    return rank_str.upper(), summoner_name, success

def main():	
	with open('./settings.json') as f:
	
		settings = json.load(f)
    
	client.run(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
	main()
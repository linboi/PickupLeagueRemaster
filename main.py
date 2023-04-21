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
    
    # Signup command
    if(message.content.startswith('!signup')):
        # Remove command from msg
        msg_content = message.content
        msg_content = msg_content.replace("!signup", "")
        
        # Scrape op.gg link
        pRank, pName, signUpSuccess = await opggWebScrape(msg_content, message)
        
        # Give access to '#select-roles' channel
        if(signUpSuccess):
            await message.channel.send(f"{pName}" + " (" + f"{pRank})")
        else:
            await message.channel.send(pRank + " (" + pName + ") \nFailed 😔 please try again!")
        
# Select Role based on Reaction 
@client.event
async def on_raw_reaction_add(reaction):
    
    # Message ID's for #select-role channel
    primary_role_message = '1098222182997442611'
    secondary_role_message = '1098680816961335408'
    
    # Select PRIMARY ROLE 
    if reaction.channel_id == select_role_channel.id and str(reaction.message_id) == primary_role_message:
        # Jungle Selected
        if str(reaction.emoji) == "✨"  : 
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their primary role to JNG") 
            await updatePlayerRole(reaction.user_id, 1, "JNG")   
        # Mid Selected
        elif str(reaction.emoji) == "😎"  : 
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their primary role to MID")
            await updatePlayerRole(reaction.user_id, 1, "MID")   
        # Top Selected
        elif str(reaction.emoji) == "🥶"  : 
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their primary role to TOP")
            await updatePlayerRole(reaction.user_id, 1, "TOP")   
        # AD Selected
        elif str(reaction.emoji) == "😭"  :
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their primary role to ADC")
            await updatePlayerRole(reaction.user_id, 1, "ADC")   
        # Support Selected
        elif str(reaction.emoji) == "🤡"  :
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their primary role to SUP")
            await updatePlayerRole(reaction.user_id, 1, "SUP")   

    # Select SECONDARY ROLE
    if reaction.channel_id == select_role_channel.id and str(reaction.message_id) == secondary_role_message:
        # Jungle Selected
        if str(reaction.emoji) == "✨"  :
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their secondary role to JNG") 
            await updatePlayerRole(reaction.user_id, 2, "JNG")  
        # Mid Selected
        elif str(reaction.emoji) == "😎"  :
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their secondary role to MID")
            await updatePlayerRole(reaction.user_id, 2, "MID")  
        # Top Selected
        elif str(reaction.emoji) == "🥶"  :
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their secondary role to TOP")
            await updatePlayerRole(reaction.user_id, 2, "TOP")  
        # AD Selected
        elif str(reaction.emoji) == "😭"  :
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their secondary role to ADC")
            await updatePlayerRole(reaction.user_id, 2, "ADC")  
        # Support Selected
        elif str(reaction.emoji) == "🤡"  : 
            user_name = await client.fetch_user(reaction.user_id)
            await main_channel.send(f"✨ {user_name} has changed their secondary role to SUP")
            await updatePlayerRole(reaction.user_id, 2, "SUP")   
    
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
    
        # Add rank division for Masters, GM, and Challenger players
        if len(rank) == 1:
            rank.append('1')
            
        summoner_name = doc.find_all(class_="summoner-name")
        summoner_name = summoner_name[0].decode_contents().strip()
        
        # Discord ID
        discordID = message_obj.author.id
        
        # Check if player exists in Player DB, returns a boolean
        doesPlayerExist = await checkPlayerExsits(discordID)
        
        if doesPlayerExist:
            # Player already exists
            await message_obj.channel.send('😭 Player exists in the table, unable to register again!')
        else:
            # Add player
            addPlayer(discordID, summoner_name, op_url, rank)
            # Give access to #select-role text channel (change permissions)
            for guild in client.guilds:
                for member in guild.members:
                    if (member.id == message_obj.author.id):
                        overwrite = discord.PermissionOverwrite()
                        overwrite.send_messages = False
                        overwrite.read_messages = True
                        await select_role_channel.set_permissions(member, overwrite=overwrite)
                        await message_obj.channel.send(f"Success, head over to {select_role_channel.mention} to assign your Primary and Secondary role!")
        success = True
        
       
    except:
        rank_str = "Invalid Account"
        summoner_name = "Invalid Account"
        success = False
        
    return rank_str.upper(), summoner_name, success

# Check if player exists in Table DB, returns a boolean
async def checkPlayerExsits(discordID):
    
    # Check if the discordID already exists in DB
    res = cursor.execute(f"SELECT COUNT(*) FROM Player WHERE discordID = '{discordID}'")
    result = res.fetchone()
    
    if result[0] > 0:
        return True
    else:
        return False
        
# Adds player to Player & Account DB
def addPlayer(discordID, summoner_name, op_url, rank):
    
    cursor.execute(f"INSERT INTO Player (discordID, winCount, lossCount, internalRating) VALUES ({discordID}, 0, 0, 1500)")
    con.commit()
    
    # Add player account to Account table
    
    # Fetch PlayerID value from Player Table w/ DiscordID
    res = cursor.execute(f"SELECT playerID from Player where discordID={discordID}")
    fetchedPlayerID = res.fetchone()
    
    # Add information into Account Table
    
    # Name, OPGG, PID, Rank, Rank DIV
    cursor.execute(f"INSERT INTO Account (name, opgg, playerID, rankTier, rankDivision) VALUES ('{summoner_name}', '{op_url}', {fetchedPlayerID[0]}, '{rank[0]}', {rank[1]})")
    con.commit()

# Update roles of player
async def updatePlayerRole(discordID, roleType, position):
    
    # Check if player exists in DB
    doesPlayerExist = await checkPlayerExsits(discordID)
    if(doesPlayerExist):
        # Update role in DB
        
        # Primary Role
        if(roleType == 1):
            cursor.execute(f"UPDATE Player SET primaryRole = '{position}' WHERE discordID = {discordID}")
            con.commit()
            
        # Secondary Role
        else:
            cursor.execute(f"UPDATE Player SET secondaryRole = '{position}' WHERE discordID = {discordID}")
            con.commit()
    
def main():	
	with open('./settings.json') as f:
	
		settings = json.load(f)
    
	client.run(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
	main()
import requests
import discord
import timing
import datetime
import time
import asyncio
from bs4 import BeautifulSoup

class serverInstance:
	def __init__(self):
		self.queue = []

	def ready(self, client, announcementChannel, roleChannel, testChannel, cursor, con):
		self.client = client
		self.announcementChannel = announcementChannel
		self.roleChannel = roleChannel
		self.cursor = cursor
		self.con = con
		self.testChannel = testChannel
	
	async def addToQueue(self, player, channel):
		if player not in self.queue:
			self.queue.append(player)
		await channel.send(f"{len(self.queue)} players in queue.\nEstimated wait time: Literally forever")
		if len(self.queue) % 10 == 0:
			self.matchmake(self.queue)
			self.queue = []

	async def removeFromQueue(self, player, channel):
		if player in self.queue:
			self.queue.remove(player)
		await channel.send(f"{len(self.queue)} players in queue.\nEstimated wait time: Literally forever")
		if len(self.queue) % 10 == 0:
			self.matchmake(self.queue)
			self.queue = []
	
	def matchmake(self, listOfPlayers):
		#to be implemented
		pass
	
	async def createGamesOnSchedule(self, schedule, channel):
		await timing.sleep_until(schedule)
		thisGameday = {}
		for gameday in schedule:
			if gameday['Day'] == datetime.datetime.now().weekday():
				thisGameday = gameday
		timeObjs = []
		thisGameday['Times'].sort()
		for times in thisGameday['Times']:
			hours, minutes = times.split(":")
			timeObjs.append(datetime.datetime.now().replace(hour=int(hours), minute=int(minutes)))

		relativeTimeString = ""
		for idx, times in enumerate(timeObjs):
			relativeTimeString += (f"Game {idx+1}: <t:" + str(int(time.mktime(times.timetuple()))) + ":R>\n")

		checkinMessage = await channel.send(f"Check in for registered players\n\
React with the corresponding number to check in for a game\n\
{relativeTimeString}\n\
After a win, post a screenshot of the victory and type !win (only one player on the winning team must do this).\n\
")
		emojiList = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
		waitSecondsAndEmoji = []
		for idx, games in enumerate(timeObjs):
			await checkinMessage.add_reaction(emojiList[idx])
			waitSecondsAndEmoji.append(((games - datetime.datetime.now()).seconds, emojiList[idx]))
		waitSecondsAndEmoji.sort()

		gamesList = []
		for idx, timeAndEmoji in enumerate(waitSecondsAndEmoji):
			gamesList.append(self.createGames(timeAndEmoji[0], timeAndEmoji[1], channel, checkinMessage.id))

		await asyncio.gather(*gamesList)

		await self.createGamesOnSchedule(schedule, channel)
	
	async def createGames(self, numSeconds, emoji, channel, messageID):
		await asyncio.sleep(numSeconds)
		message = await channel.fetch_message(messageID)
		msg = f"Users who reacted for game {emoji}:"
		reactionList = message.reactions
		for reaction in reactionList:
			if reaction.emoji == emoji:
				async for user in reaction.users():
					msg+= "\n" + user.display_name
		await channel.send(msg)

	# Scrape rank details from op.gg page
	async def signUpPlayer(self, msg_content, message_obj):
	
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
			
			
			# Check if player suggested rank is formatted right
				
			summoner_name = doc.find_all(class_="summoner-name")
			summoner_name = summoner_name[0].decode_contents().strip()
			
			# Discord ID
			discordID = message_obj.author.id
			
			# Check if player exists in Player DB, returns a boolean
			doesPlayerExist = await self.checkPlayerExsits(discordID)
			
			if doesPlayerExist:
				# Player already exists
				await message_obj.channel.send('😭 Player exists in the table, unable to register again!')
			else:
				# Add player
				self.addPlayer(discordID, summoner_name, op_url, rank)
				# Give access to #select-role text channel (change permissions)
				for guild in self.client.guilds:
					for member in guild.members:
						if (member.id == message_obj.author.id):
							overwrite = discord.PermissionOverwrite()
							overwrite.send_messages = False
							overwrite.read_messages = True
							await self.roleChannel.set_permissions(member, overwrite=overwrite)
							await message_obj.channel.send(f"Success, head over to {self.roleChannel.mention} to assign your Primary and Secondary role!")
			success = True
			
		
		except:
			rank_str = "Invalid Account"
			summoner_name = "Invalid Account"
			success = False
			
		return rank_str.upper(), summoner_name, success

	# Add other accounts
	async def addAccount(self, msg_content, message_obj):
		
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
			doesPlayerExist = await self.checkPlayerExsits(discordID)
			
			if doesPlayerExist:
				# Player already exists, add account
				self.addExtraAccount(discordID, summoner_name, op_url, rank)
				success = True
			else:
				rank_str = "Signup first before adding an account!"
				summoner_name = "Invalid Account"
				success = False
			
			
		
		except:
			rank_str = "Signup first before adding an account!"
			summoner_name = "Invalid Account"
			success = False
			
		return rank_str.upper(), summoner_name, success




 	# Check if player exists in Table DB, returns a boolean
	async def checkPlayerExsits(self, discordID):
		
		# Check if the discordID already exists in DB
		res = self.cursor.execute(f"SELECT COUNT(*) FROM Player WHERE discordID = '{discordID}'")
		result = res.fetchone()
		
		if result[0] > 0:
			return True
		else:
			return False
			
	# Adds player to Player & Account DB
	def addPlayer(self, discordID, summoner_name, op_url, rank):
		
		self.cursor.execute(f"INSERT INTO Player (discordID, winCount, lossCount, internalRating) VALUES ({discordID}, 0, 0, 1500)")
		self.con.commit()
		
		# Add player account to Account table
		
		# Fetch PlayerID value from Player Table w/ DiscordID
		res = self.cursor.execute(f"SELECT playerID from Player where discordID={discordID}")
		fetchedPlayerID = res.fetchone()
		
		# Add information into Account Table
		
		# Name, OPGG, PID, Rank, Rank DIV
		self.cursor.execute(f"INSERT INTO Account (name, opgg, playerID, rankTier, rankDivision) VALUES ('{summoner_name}', '{op_url}', {fetchedPlayerID[0]}, '{rank[0]}', {rank[1]})")
		self.con.commit()
  
	# Adds another Account to Account DB
	def addExtraAccount(self, discordID, summoner_name, op_url, rank):
		
		# Add player account to Account table
		
		# Fetch PlayerID value from Player Table w/ DiscordID
		res = self.cursor.execute(f"SELECT playerID from Player where discordID={discordID}")
		fetchedPlayerID = res.fetchone()
		
		# Add information into Account Table
		
		# Name, OPGG, PID, Rank, Rank DIV
		self.cursor.execute(f"INSERT INTO Account (name, opgg, playerID, rankTier, rankDivision) VALUES ('{summoner_name}', '{op_url}', {fetchedPlayerID[0]}, '{rank[0]}', {rank[1]})")
		self.con.commit()
	
	# Update roles of player
	async def updatePlayerRole(self, reaction, roleType, position):
		
		# Set discordID of reaction
		discordID = reaction.user_id
		
		# Fetch Player's Username
		user_name = await self.client.fetch_user(reaction.user_id)
		# Check if player exists in DB
		doesPlayerExist = await self.checkPlayerExsits(discordID)
		if(doesPlayerExist):
			# Update role in DB
			
			# Primary Role
			if(roleType == 1):
				
				# Check if duplicate position
				canChangeRole = self.checkDupPos(discordID, roleType, position)
				if canChangeRole:
					self.cursor.execute(f"UPDATE Player SET primaryRole = '{position}' WHERE discordID = {discordID}")
					self.con.commit()
					await self.testChannel.send(f"✨ {user_name} has changed their PRIMARY role to {position}")
				else:
					await self.testChannel.send(f"✨ {user_name}'s SECONDARY role is already set to {position} ")
				
			# Secondary Role
			else:
				
				# Check if duplicate position
				canChangeRole = self.checkDupPos(discordID, roleType, position)
				if canChangeRole:
					self.cursor.execute(f"UPDATE Player SET secondaryRole = '{position}' WHERE discordID = {discordID}")
					self.con.commit()
					await self.testChannel.send(f"✨ {user_name} has changed their SECONDARY role to {position}")
				else:
					await self.testChannel.send(f"✨ {user_name}'s PRIMARY role is already set to {position}")

	# Function called when player reacts to a role selection
	async def changePlayerRole(self, reaction):
		# Message ID's for #select-role channel
		primary_role_message = '1098222182997442611'
		secondary_role_message = '1098680816961335408'
		
		# Select PRIMARY ROLE 
		if reaction.channel_id == self.roleChannel.id and str(reaction.message_id) == primary_role_message:
			# Jungle Selected
			if str(reaction.emoji) == "✨"  : 
				await self.updatePlayerRole(reaction, 1, "JNG")   
			# Mid Selected
			elif str(reaction.emoji) == "😎"  : 
				await self.updatePlayerRole(reaction, 1, "MID")   
			# Top Selected
			elif str(reaction.emoji) == "🥶"  : 
				await self.updatePlayerRole(reaction, 1, "TOP")   
			# AD Selected
			elif str(reaction.emoji) == "😭"  :
				await self.updatePlayerRole(reaction, 1, "ADC")   
			# Support Selected
			elif str(reaction.emoji) == "🤡"  :
				await self.updatePlayerRole(reaction, 1, "SUP")   

		# Select SECONDARY ROLE
		if reaction.channel_id == self.roleChannel.id and str(reaction.message_id) == secondary_role_message:
			# Jungle Selected
			if str(reaction.emoji) == "✨"  :
				await self.updatePlayerRole(reaction, 2, "JNG")  
			# Mid Selected
			elif str(reaction.emoji) == "😎"  :
				await self.updatePlayerRole(reaction, 2, "MID")  
			# Top Selected
			elif str(reaction.emoji) == "🥶"  :
				await self.updatePlayerRole(reaction, 2, "TOP")  
			# AD Selected
			elif str(reaction.emoji) == "😭"  :
				await self.updatePlayerRole(reaction, 2, "ADC")  
			# Support Selected
			elif str(reaction.emoji) == "🤡"  : 
				await self.updatePlayerRole(reaction, 2, "SUP")  
	 
	# Check if position is aleady set in other role
	def checkDupPos(self, discordID, newRoleType, position):
		
		# Get position in other roleType
		if newRoleType == 1:
			res = self.cursor.execute(f"SELECT secondaryRole FROM Player WHERE discordID = {discordID}")
			currentPosition = res.fetchone()
			if currentPosition[0] != position:
				return True
			else:
				return False
			
		elif newRoleType == 2:
			res = self.cursor.execute(f"SELECT primaryRole FROM Player WHERE discordID = {discordID}")
			currentPosition = res.fetchone()
			if currentPosition[0] != position:
				return True
			else:
				return False
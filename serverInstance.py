import requests
import discord
import timing
import datetime
from datetime import date
import time
import asyncio
from bs4 import BeautifulSoup
from player import Player
from match import Match
from team import Team
import random


class serverInstance:
	def __init__(self):
		self.queue = []

	def ready(self, client, roleChannel, testChannel, announcementChannel, generalChannel, voiceChannels, primaryRoleMsg, secondaryRoleMsg, cursor, con):
		self.client = client
		self.announcementChannel = announcementChannel
		self.roleChannel = roleChannel
		self.cursor = cursor
		self.con = con
		self.testChannel = testChannel
		self.generalChannel = generalChannel
		self.voiceChannels = voiceChannels
		self.primaryRoleMSG = primaryRoleMsg
		self.secondaryRoleMSG = secondaryRoleMsg
		self.currentMatches = []
		self.playerIDNameMapping = {}
	
	async def addToQueue(self, player, channel):
		if player not in self.queue:
			self.queue.append(player)
		await channel.send(f"{len(self.queue)} players in queue.\nEstimated wait time: Literally forever")
		if len(self.queue) % 10 == 0:
			matches = await self.matchmakeV2(self.queue)
			self.currentMatches.extend(matches)
			await self.announcementChannel.send(str(matches))
			self.queue = []

	async def removeFromQueue(self, player, channel):
		if player in self.queue:
			self.queue.remove(player)
		await channel.send(f"{len(self.queue)} players in queue.\nEstimated wait time: Literally forever")
	
	# Mehtod which creates Matches based on available Players
	async def matchmake(self, playerIDList):
	 	# List of all players in Queue
		listypoo = []
		for player in playerIDList:
			listypoo.append(player)
		res = self.cursor.execute("SELECT * FROM Player")# WHERE discordID in ({seq})".format(seq=','.join(['?']*len(playerIDList))))
		listOfPlayers = res.fetchall()
		shorterlist = []
		for player in listOfPlayers:
			if player[1] in playerIDList:
				shorterlist.append(player)
		listOfPlayers = shorterlist
		# Create a Player obj for each Player in Queue 
		playerObjList = []
		for player_details in listOfPlayers:
			discordUser = None
			try:
				discordUser = await self.client.fetch_user(player_details[1])
			except:
				discordUser = None
			player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                   player_details[9], player_details[10], player_details[11], self.cursor, self.con, discordUser)
			# Add player to list
			playerObjList.append(player)
   
		players_in_queue = len(playerObjList)
		
		# Number of macthes to create
		match_count = players_in_queue // 10
		
		# Number of players required
		required_players = match_count * 10
	
		# Shuffle players
		tempMatch = Match(self.cursor, self.con)
		# Ordered QP List & add PQP for players who were left out
		ordered_pq_list = tempMatch.shuffle_orderPQ(playerObjList, required_players)
	
		for player in ordered_pq_list:
			# Reset QP of selected players
			print(f"[{player.get_pID()}], [{player.get_QP()}]")
		# Ordered Rank List
		ordered_mmr_list = tempMatch.orderBasedOnMMR(ordered_pq_list)

			
   
		# Init Match(s)
		# For each match, set roles and find fairest comobination of players
  
		while len(self.currentMatches) < match_count:
			# Get top 10 players
			mCount = len(self.currentMatches) + 1
			# Init a Match 
			initMatch = Match(self.cursor, self.con)
			# Shuffle Selected Players
			ordered_player_list = ordered_mmr_list[((mCount-1)*10):(mCount*10)]
			shuffled_list = sorted(ordered_player_list, key=lambda k: random.random())
			# Assign roles for players & set roleMMR
			assigned_roles = initMatch.fitRoles(shuffled_list)
			
			# Set roles for each team in match
			initMatch.setInitTeams(assigned_roles)
			# Find fairest combination of players
			initMatch.findFairestTeams()
			# Add Match to Match Table & Give it an ID
			initMatch.insert()
			# Add match to list of current games
			print("please run " + str(initMatch))
			self.currentMatches.append(initMatch)
			print("please run " + str(self.currentMatches))
			

		
		await self.displayMatch()
		
	# Display current matches on discord channel
	async def displayMatch(self):
		#await self.testChannel.send(f"**__Current Matches__**:\n")
		for match in self.currentMatches:
			# Display Details of Match
			msg = await self.testChannel.send(f"{match.displayMatchDetails()}\n")
			await msg.edit(suppress=True)
			await self.testChannel.send(f"---------------------------------------------")
	
			# Send DM to all players
			user_list = match.listOfUsers()
			for user in user_list:
				# Check if user is in member list
				try:
					memberFound = self.client.guilds[0].get_member(user)
					if memberFound:
						await memberFound.send(f"✨ You have been picked for a game, head over to {self.testChannel.mention} to see the teams!")
				except:
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

		await self.triggerGamesAtGivenTimes(timeObjs, channel)

		await self.createGamesOnSchedule(schedule, channel)

	async def triggerGamesAtGivenTimes(self, timeObjs, channel):
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

	async def unscheduledGames(self, minutesUntil):
		timeObjs = []
		for minutes in minutesUntil:
			timeObjs.append(datetime.datetime.now() + datetime.timedelta(minutes=int(minutes)))
		await self.triggerGamesAtGivenTimes(timeObjs, self.announcementChannel)
	
	async def createGames(self, numSeconds, emoji, channel, messageID):
		await asyncio.sleep(numSeconds)
		message = await channel.fetch_message(messageID)
		msg = f"Users who reacted for game {emoji}:"
		playerIDs = []
		reactionList = message.reactions
		for reaction in reactionList:
			if reaction.emoji == emoji:
				async for user in reaction.users():
					playerIDs.append(user.id)
		
		matches = await self.matchmakeV2(playerIDs)
		self.currentMatches.extend(matches)
		match_string = str(matches).replace("[", "")
		match_string = match_string.replace("]", "")
		msg = await channel.send(match_string)
		await msg.edit(suppress=True)
  
	async def mmTest(self):
		discord_id_list = [197057417358475264, 197058147167371265, 127796716408799232, 180398163620790279, 225650967058710529, 618520923204485121, 160471312517562368, 188370105413926912, 694560846814117999, 266644132825530389]
		matches = await self.matchmakeV2(discord_id_list)
		self.currentMatches.extend(matches)
		match_string = str(matches).replace("[", "")
		match_string = match_string.replace("]", "")
		msg = await self.testChannel.send(match_string)
		await msg.edit(suppress=True)

	async def win(self, message):
		activePlayerMatches = []
		activePlayer = message.author.id
		for match in self.currentMatches:
			for player in match.blueTeam.getListPlayers():
				if player.get_dID() == activePlayer:
					activePlayerMatches.append((match, 'BLUE'))
			for player in match.redTeam.getListPlayers():
				if player.get_dID() == activePlayer:
					activePlayerMatches.append((match, 'RED'))

		if len(activePlayerMatches) == 0:
			await message.channel.send("Player not found in any active matches")
		if len(activePlayerMatches) == 1:
			activePlayerMatches[0][0].resolve(activePlayerMatches[0][1])
			self.currentMatches.remove(activePlayerMatches[0][0])
			await message.channel.send("🎊 WPGG, remember to upload a post-game screenshot!")
		if len(activePlayerMatches) > 1:
			await message.channel.send("Player found in more than one match, uh oh")

	# Scrape rank details from op.gg page
	async def signUpPlayer(self, msg_content, message_obj):
	
		# Assign Headers, so scraping is not BLOCKED
		headers = requests.utils.default_headers()
		headers.update({
				'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
		})
		
		# Try scrape OP.GG URL
		try:
			op_url = msg_content.strip()
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
			lp = doc.find_all(class_="lp")
			lp = lp[0].decode_contents().strip()
			lp = lp.replace("<!-- -->", "")
			lp = lp.split()
			lp = lp[0]
			lp = lp.replace(",", "")

			print(int(lp))
		
			rank_str = ""
			for char in rank:
				rank_str += char[0]
		
			# Add rank division for Masters, GM, and Challenger players
			if len(rank) == 1:
				rank.append(lp)
				rank_str += f" {lp}LP"
			
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
				try:
					for guild in self.client.guilds:
						for member in guild.members:
							if (member.id == message_obj.author.id):
								# Access to role channel
								overwrite_role = discord.PermissionOverwrite()
								overwrite_role.send_messages = False
								overwrite_role.read_messages = True
								overwrite_role.read_message_history = True
								await self.roleChannel.set_permissions(member, overwrite=overwrite_role)
								# Access to other channels
								overwrite_general = discord.PermissionOverwrite()
								overwrite_general.send_messages = True
								overwrite_general.read_messages = True
								overwrite_general.read_message_history = True
								await self.announcementChannel.set_permissions(member, overwrite=overwrite_role)
								await self.generalChannel.set_permissions(member, overwrite=overwrite_general)
								# Access to voice channels
								overwrite_voice = discord.PermissionOverwrite()
								overwrite_voice.connect = True
								overwrite_voice.send_messages = True
								overwrite_voice.read_message_history = True
								overwrite_voice.speak = True
								overwrite_voice.read_messages = True
								overwrite_voice.stream = True
								# 1-n voice channels
								# Add each one from list
								#for channel in self.voiceChannels:
									#voip = int(channel)
									#await voip.set_permissions(member, overwrite=overwrite_voice)
								await message_obj.channel.send(f"🥳 Success {member.mention} head over to {self.roleChannel.mention} to assign your **Primary** and **Secondary** role!")
				except discord.Forbidden:
					print("Forbidden")
				except:
					print("other")
			success = True
			
		
		except:
			rank_str = "Invalid Account + Channel Issue"
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
			op_url = msg_content.strip()
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
   
			lp = doc.find_all(class_="lp")
			lp = lp[0].decode_contents().strip()
			lp = lp.replace("<!-- -->", "")
			lp = lp.split()
			lp = lp[0]
			lp = lp.replace(",", "")

   
			rank_str = ""
			for char in rank:
				rank_str += char[0]
		
			# Add rank division for Masters, GM, and Challenger players
			if len(rank) == 1:
				rank.append(lp)
				
				
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
				rank_str = "Signup first before adding an account1!"
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
		
		self.cursor.execute(f"INSERT INTO Player (discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, isAdmin, missedGames, signupCount, leaderboardPoints) VALUES ({discordID}, 0, 0, 1500, 'FILL', 'FILL', 0, 0, 0, 1200)")
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
	async def updatePlayerRole(self, discordID, roleType, position):
		
		# Fetch Player's Username
		user_name = await self.client.fetch_user(discordID)
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

	async def roles(self, message):
		roleMsg = await message.author.send("Choose your primary role:\n🥶 - TOP\n✨ - JG\n😎  - MID\n😭 - AD\n🤡  - SUP\n🤔  - FILL\n\nyou can change your role in the future, use !roles again.")
		roleMapping = {
				'🥶' : 'TOP',
				'✨' : 'JNG',
				'😎' : 'MID',
				'😭' : 'ADC',
				'🤡' : 'SUP',
				'🤔': 'FILL'
			}
		for react in roleMapping:
			await roleMsg.add_reaction(react)

		def check(reaction, user):
			return (reaction.message.id == roleMsg.id and user == message.author and reaction.emoji in roleMapping)

		primaryRole, user = await self.client.wait_for('reaction_add', check=check)
		await message.author.send("Now choose secondary role")
		secondaryRole, _ = await self.client.wait_for('reaction_add', check=check)
		print("got here")
		await self.updatePlayerRole(user.id, 1, roleMapping[primaryRole.emoji])
		await self.updatePlayerRole(user.id, 2, roleMapping[secondaryRole.emoji])


	# Function called when player reacts to a role selection
	async def changePlayerRole(self, reaction):
		# Message ID's for #select-role channel
		primary_role_message = self.primaryRoleMSG
		secondary_role_message = self.secondaryRoleMSG
		
		# Select PRIMARY ROLE 
		if reaction.channel_id == self.roleChannel.id and str(reaction.message_id) == primary_role_message:
			# Jungle Selected
			if str(reaction.emoji) == "✨"  : 
				await self.updatePlayerRole(reaction.user_id, 1, "JNG")   
			# Mid Selected
			elif str(reaction.emoji) == "😎"  : 
				await self.updatePlayerRole(reaction.user_id, 1, "MID")   
			# Top Selected
			elif str(reaction.emoji) == "🥶"  : 
				await self.updatePlayerRole(reaction.user_id, 1, "TOP")   
			# AD Selected
			elif str(reaction.emoji) == "😭"  :
				await self.updatePlayerRole(reaction.user_id, 1, "ADC")   
			# Support Selected
			elif str(reaction.emoji) == "🤡"  :
				await self.updatePlayerRole(reaction.user_id, 1, "SUP")
			# Fill Selected
			elif str(reaction.emoji) == "🤔"  :
				await self.updatePlayerRole(reaction.user_id, 1, "FILL")

		# Select SECONDARY ROLE
		if reaction.channel_id == self.roleChannel.id and str(reaction.message_id) == secondary_role_message:
			# Jungle Selected
			if str(reaction.emoji) == "✨"  :
				await self.updatePlayerRole(reaction.user_id, 2, "JNG")  
			# Mid Selected
			elif str(reaction.emoji) == "😎"  :
				await self.updatePlayerRole(reaction.user_id, 2, "MID")  
			# Top Selected
			elif str(reaction.emoji) == "🥶"  :
				await self.updatePlayerRole(reaction.user_id, 2, "TOP")  
			# AD Selected
			elif str(reaction.emoji) == "😭"  :
				await self.updatePlayerRole(reaction.user_id, 2, "ADC")  
			# Support Selected
			elif str(reaction.emoji) == "🤡"  : 
				await self.updatePlayerRole(reaction.user_id, 2, "SUP")  
			# Fill Selected
			elif str(reaction.emoji) == "🤔"  :
				await self.updatePlayerRole(reaction.user_id, 2, "FILL")
	 
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

	# Method to get players rank and show it in discord channel
	async def displayRank(self, message_obj):
			discordID = message_obj.author.id
			res = self.cursor.execute(f"SELECT leaderboardPoints, winCount, lossCount FROM Player WHERE discordID = {discordID}")
			mmr = res.fetchone()
			res = self.cursor.execute(f"SELECT discordID FROM Player ORDER BY leaderboardPoints DESC")
			output = res.fetchall()
			test = []
			for rank in output:
				test.append(rank[0])
			await message_obj.channel.send(f"*Current Rank* **#{test.index(discordID) + 1}**\t{message_obj.author.mention}\t{round(mmr[0])}**LP**\t({round(mmr[1])}**W**/{round(mmr[2])}**L**)")
   
	# Method to display Leaderboard
	async def displayLeaderboard(self, channelToSendIn, pageNum=0, message=None):
		res = self.cursor.execute(f"SELECT discordID, winCount, lossCount, leaderboardPoints, ROW_NUMBER() OVER (ORDER BY leaderboardPoints DESC), primaryRole, secondaryRole FROM Player ORDER BY leaderboardPoints DESC")
		output = res.fetchall()
		all_players = ""
		pageNum = min(pageNum, len(output)//20)
		pageNum = max(pageNum, 0)
		toPosition = min((pageNum+1)*20, len(output))
		fromPosition = pageNum*20

		for player in output[fromPosition:toPosition:]:
			if player[0] not in self.playerIDNameMapping:
				try:
					discord_name = (await self.client.fetch_user(player[0])).display_name
				except:
					discord_name = player[0]
				self.playerIDNameMapping[player[0]] = discord_name
				print(discord_name)
			else:
				discord_name = self.playerIDNameMapping[player[0]]
			pos = f"#{player[4]}"
			pos = pos.ljust(5)
			id = f"{discord_name}"
			id = id.ljust(20)
			win = f"\t({player[1]}W"
			win = win.rjust(6)
			loss = f"{player[2]}L)"
			leaderboardPoints = f"{int(player[3])}LP"
			leaderboardPoints = leaderboardPoints.ljust(8)
			pRole = player[5]
			sRole = player[6]

			all_players += f"{pos}" + f"{id}" + f"{leaderboardPoints}" + f"{win}/" + f"{loss} ({pRole}/{sRole})\n"

   
		now = date.today()
		if message == None:
			message = await channelToSendIn.send(f"**__Updated Leaderboard__***\t\tLast Updated: {now}*```{all_players}```")
			await message.add_reaction('⬅')
			await message.add_reaction('➡')
		else:
			await message.edit(content=f"**__Updated Leaderboard__***\t\tLast Updated: {now}*```{all_players}```")

		def check(reaction, user):
			return reaction.message.id == message.id and reaction.emoji in ['⬅', '➡']

		try:
			emoji, user = await self.client.wait_for('reaction_add', check=check, timeout=300)
			await emoji.remove(user)
		except asyncio.TimeoutError:
			await message.clear_reactions()
			return
		
		if emoji.emoji == '⬅':
			await self.displayLeaderboard(channelToSendIn, pageNum=pageNum-1, message=message)
		elif emoji.emoji == '➡':
			await self.displayLeaderboard(channelToSendIn, pageNum=pageNum+1, message=message)


  
	# Method to End a Current Match if not started or void
	async def endMatch(self, message_obj, matchID): 
		# Check if admin
		admin_check = await self.checkAdmin(message_obj.author.id)
		if admin_check:
			# Check if matchID is in current matches
			for match in self.currentMatches:
				match_id = match.get_matchID()
				try:
					if match_id == int(matchID):
						# Delete Match
						match.delete()
						# Pop match off list
						self.currentMatches.remove(match)
						await message_obj.channel.send(f"🗑️ Match ({match_id}) Removed")
				except:
					pass

	# Method to punish a player -> reducing LP and QP
	async def punishPlayer(self, message_obj, discordID):
		
		# Check if admin
		admin_check = await self.checkAdmin(message_obj.author.id)
		if admin_check:
			discordID = discordID.replace("<@", "")
			discordID = discordID.replace(">", "")
			res = self.cursor.execute(f"SELECT leaderboardPoints, signupCount, discordID FROM Player WHERE discordID = {discordID}")
			result = res.fetchone()
			new_mmr = result[0] - 50
			add_signupCount = result[1] + 3
			user = await self.client.fetch_user(discordID)
			self.cursor.execute(f"UPDATE Player SET leaderboardPoints = {new_mmr}, signupCount = {add_signupCount} WHERE discordID = {discordID}")
			self.con.commit()
			await message_obj.channel.send(f"🔨 {user.mention} has been given a penalty of -50**LP** and added to **Low Priority Queue**")
		
	# Method to swap two players on the same team
	async def swapPlayers(self, message_obj, discordIDOtherPlayer):
		discordIDPlayer = message_obj.author.id 
		discordIDOtherPlayer = discordIDOtherPlayer.replace("<@", "")
		discordIDOtherPlayer = discordIDOtherPlayer.replace(">", "")
		try:
			reaction, res = await self.client.wait_for(
				"reaction_add",
				check=lambda y, x: y.message.channel.id == message_obj.channel.id
				and str(x.id) == str(discordIDPlayer)
				and y.emoji == "✨",
				timeout=60.0,)
	
			if str(reaction.emoji) == "✨":
				for match in self.currentMatches:
					try:
						await match.swapPlayers(discordIDPlayer, discordIDOtherPlayer, message_obj)
					except:
						pass
		except asyncio.TimeoutError:
			await message_obj.channel.send(f"Swap timed out {message_obj.author.mention}")
   
   
	async def replacePlayer(self, msg_obj, discordIDOrigin, discordIDReplacement):
     
		# Check called by (isAdmin)
		user_id = msg_obj.author.id
		admin_check = await self.checkAdmin(user_id)
		if admin_check:
			# Parse discord ID's from mentions in message
			discordIDOrigin = discordIDOrigin.replace("<@", "")
			discordIDOrigin = discordIDOrigin.replace(">", "")
			discordIDReplacement = discordIDReplacement.replace("<@", "")
			discordIDReplacement = discordIDReplacement.replace(">", "")
			# Check for players in every match -> if found, replace player
			for match in self.currentMatches:
				try:
					await match.swapPlayers(discordIDOrigin, discordIDReplacement, msg_obj)
					await msg_obj.channel.send(f"Replace Successful")
				except:
					await msg_obj.channel.send(f"Replacement Error")
		else:
			pass
			
		
	# Check if discordID is Admin
	async def checkAdmin(self, discordID):
		res = self.cursor.execute(f"SELECT isAdmin FROM Player WHERE discordID = {discordID}")
		result = res.fetchone()
		if(result[0] == 1):
			return True
		else:
			return False
			
	def getTotalMMR(self, team):
		total = 0
		for player, role in team:
			total += player.getMMRinRole(role)

		return total

	# discordUser is None, isn't used either. Should maybe fix this idk 
	async def matchmakeV2(self, playerIDList):
		# List of all players in Queue
		res = self.cursor.execute("SELECT * FROM Player")# WHERE discordID in ({seq})".format(seq=','.join(['?']*len(playerIDList))))
		listOfPlayers = res.fetchall()
		shorterlist = []
		for player in listOfPlayers:
			if player[1] in playerIDList:
				shorterlist.append(player)
		listOfPlayers = shorterlist
		print("Shoter List Compiled:" + str(len(shorterlist)))
		playerObjList = []
		for player_details in listOfPlayers:
			discordUser = None
			try:
				discordUser = await self.client.fetch_user(player_details[1])
			except:
				discordUser = None
			player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                   player_details[9], player_details[10], player_details[11], self.cursor, self.con, discordUser)
			# Add player to list
			playerObjList.append(player)
   
		players_in_queue = len(playerObjList)
		
		# Number of macthes to create
		match_count = players_in_queue // 10

		team_count = match_count * 2
		
		# Number of players required
		required_players = match_count * 10

		# up to here was your code @cail
		# Static players in queue list duplicate
		init_player_list = playerObjList

		# step 1
		def getRatioOfMissedGames(player):
			if player.get_signUpCount() == 0:
				return 1
			return player.get_missedGameCount()/player.get_signUpCount()
		
		# /step 1
		playerObjList.sort(key=getRatioOfMissedGames, reverse=True)
		for player in playerObjList:
			player.addSignUpCount()

		# step 2
		playersInRoles = {'TOP':[], 'JNG':[], 'MID':[], 'ADC':[], 'SUP':[]}
		usedPlayers = []
		for player in playerObjList:
			if player.get_pRole() in playersInRoles:
				if len(playersInRoles[player.get_pRole()]) < team_count:
					playersInRoles[player.get_pRole()].append(player)
					usedPlayers.append(player)
		playerObjList = [player for player in playerObjList if player not in usedPlayers]	# this is just remaining players now
		
		# Now put in the FILL primaries
		# Find them
		fillPlayers = []
		for player in playerObjList:
			if player.get_pRole() == "FILL":
				fillPlayers.append(player)
		playerObjList = [player for player in playerObjList if player not in fillPlayers]	# this is just remaining non fill primary players now
		
		# place them into teams
		fillIndex = 0
		for key in playersInRoles:
			while len(playersInRoles[key]) < team_count and fillIndex < len(fillPlayers):
				playersInRoles[key].append(fillPlayers[fillIndex])
				fillIndex += 1
		
		# At this point either the list of fill players should be empty or the teams should be full

		# /step 2

		# step 3
		remainingPlayersNeeded = 0
		for key in playersInRoles:
			remainingPlayersNeeded += team_count - len(playersInRoles[key]) 
		# /step 3

		# step 4 bonus step goes here, I'm not doing it tonight. Instead we'll just grab the exact num of players we need
		playerObjList.sort(key=getRatioOfMissedGames, reverse=True)
		for player in playerObjList[remainingPlayersNeeded:]:
			#player.addGameMissed()
			print("MG +1")
		playerObjList = playerObjList[:remainingPlayersNeeded]
		# /step 4

		# step 5: fill remaining players into roles. we should use people's secondary roles if possible here, and use fill players last
		# first we do people's secondary roles
		usedPlayers = []
		for player in playerObjList:
			if player.get_sRole() in playersInRoles:
				if len(playersInRoles[player.get_sRole()]) < team_count:
					playersInRoles[player.get_sRole()].append(player)
					usedPlayers.append(player)
		playerObjList = [player for player in playerObjList if player not in usedPlayers]	# this is just remaining players now

		# next we just put everyone else into any role, these are fill players or players who are being autofilled
		remainingPlayerIndex = 0
		for key in playersInRoles:
			while len(playersInRoles[key]) < team_count and remainingPlayerIndex < len(playerObjList):
				playersInRoles[key].append(playerObjList[remainingPlayerIndex])
				remainingPlayerIndex += 1

		#print(playersInRoles)
		# /step 5
		#At this point we should have a dictionary with keys of the 5 roles, where the values are lists of players of length (team_count)

		# step 6
		# what we're going to do here is try every combination of swapping players WITHIN THEIR ASSIGNED ROLES to find the closest set of matches
		bestMaxMMRdiff = 999999999		# Starting MMR diff unreasonably high so that it gets replaced

		#for top in playersInRoles["TOP"]:
		#	for jng in playersInRoles["JNG"]:
		#		for mid in playersInRoles["MID"]:
		#			for adc in playersInRoles["ADC"]:
		#				teamList = []
		#				for sup in playersInRoles["SUP"]:
		#					team = ((top, "TOP"), (jng, "JNG"), (mid, "MID"), (adc, "ADC"), (sup, "SUP"))
		#					avgMMR = self.getTotalMMR(team)/5
		#					teamList.append((team, avgMMR))
		#				
		#				idx = 0
		#				maxDiffBetweenTeams = 0
		#				while idx+1 < len(teamList):
		#					if abs(teamList[idx][1] - teamList[idx+1][1]) > maxDiffBetweenTeams:
		#						maxDiffBetweenTeams = abs(teamList[idx][1] - teamList[idx+1][1])
		#					idx += 2
#
		#				print("beep boop" + str(maxDiffBetweenTeams))225650967058710529
		#				if maxDiffBetweenTeams < bestMaxMMRdiff:
		#					print("here" + str(maxDiffBetweenTeams))
		#					bestMaxMMRdiff = maxDiffBetweenTeams
		#					bestMatches = []
		#					idx = 0
		#					while idx+1 < len(teamList):
		#						print("here?")
		#						blueTeam = Team(teamList[idx][0][0][0], teamList[idx][0][1][0], teamList[idx][0][2][0], teamList[idx][0][3][0], teamList[idx][0][4][0])
		#						redTeam = Team(teamList[idx+1][0][0][0], teamList[idx+1][0][1][0], teamList[idx+1][0][2][0], teamList[idx+1][0][3][0], teamList[idx+1][0][4][0])
		#						bestMatches.append(Match(self.cursor, self.con, matchID=0, blueTeam=blueTeam, redTeam=redTeam, startTime=datetime.datetime.now()))			
		#						idx += 2
		#return bestMatches
		print(playersInRoles)
		for x in range(team_count**5):
			teamList = []
			for y in range(team_count):
				top = playersInRoles["TOP"][(((x//team_count**4)%team_count)+y)%team_count]
				jng = playersInRoles["JNG"][(((x//team_count**3)%team_count)+y)%team_count]
				mid = playersInRoles["MID"][(((x//team_count**2)%team_count)+y)%team_count]
				adc = playersInRoles["ADC"][(((x//team_count**1)%team_count)+y)%team_count]
				sup = playersInRoles["SUP"][(((x//team_count**0)%team_count)+y)%team_count]

				team = ((top, "TOP"), (jng, "JNG"), (mid, "MID"), (adc, "ADC"), (sup, "SUP"))
				avgMMR = self.getTotalMMR(team)/5
				teamList.append((team, avgMMR))
			
			idx = 0
			maxDiffBetweenTeams = 0
			while idx+1 < len(teamList):
				if abs(teamList[idx][1] - teamList[idx+1][1]) > maxDiffBetweenTeams:
					maxDiffBetweenTeams = abs(teamList[idx][1] - teamList[idx+1][1])
				idx += 2

			#print("beep boop" + str(maxDiffBetweenTeams))
			if maxDiffBetweenTeams < bestMaxMMRdiff:
				bestMaxMMRdiff = maxDiffBetweenTeams
				bestMatches = []
				idx = 0
				while idx+1 < len(teamList):
					blueTeam = Team(teamList[idx][0][0][0], teamList[idx][0][1][0], teamList[idx][0][2][0], teamList[idx][0][3][0], teamList[idx][0][4][0])
					redTeam = Team(teamList[idx+1][0][0][0], teamList[idx+1][0][1][0], teamList[idx+1][0][2][0], teamList[idx+1][0][3][0], teamList[idx+1][0][4][0])
					bestMatches.append(Match(self.cursor, self.con, matchID = len(bestMatches) + 1 + datetime.datetime.now().hour, blueTeam=blueTeam, redTeam=redTeam, startTime=str(datetime.datetime.now().date()) + ", " + str(datetime.datetime.now().hour) + ":00"))	
					idx += 2
		print(f"After comparing {team_count**5} possibities across {(team_count**5)*4} teams, lowest max mmr diff found was {bestMaxMMRdiff}")
		for match in bestMatches:
				# Check if user is in member list
				pIDs = match.listOfUsers()
				for player in pIDs:
					try:
						memberFound = self.client.guilds[0].get_member(player)
						if memberFound:
							# Send the player a DM if found!
							pass
							#await memberFound.send(f"✨ You have been picked for a game, head over to {self.announcementChannel.mention} to see the teams!")
						else:
							print("Player not found as a member")
					except:
						pass
  
		# List of all players in current Matches
		playersInMatch = []
		for match in bestMatches:
			playersInMatch = match.listOfUsers()
		
		# Add missedGames() to player not in Matches
		for player in init_player_list:
			if player.get_dID() not in playersInMatch:
				player.addGameMissed()
    
		return bestMatches
		# \step 6



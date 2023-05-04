
from player import Player
from team import Team
from match import Match

class commands:
	COMMAND_SYMBOL = "!"
	
	async def hello(message, inst, args):
		print("working")
		await message.channel.send("hiya")

	async def queue(message, inst, args):
		user_id = message.author.id
		admin_check = await inst.checkAdmin(user_id)
		if not admin_check:
			return
		await inst.addToQueue(message.author.id, message.channel)

	async def dequeue(message, inst, args):
		await inst.removeFromQueue(message.author.id, message.channel)

	async def signup(message, inst, args):
		pRank, pName, signUpSuccess = await inst.signUpPlayer(args[0], message)
		print(pRank)
		print(pName)
		# Give access to '#select-roles' channel
		if(signUpSuccess == False):
			await message.channel.send("Failed 😔 please try again!")
   
	async def addAccount(message, inst, args):
		pRank, pName, signUpSuccess = await inst.addAccount(args[0], message)
  
		if signUpSuccess:
			await message.channel.send("🗃️ Account Added: " + pName)
		else:
			await message.channel.send(pName + " (" + pRank + ")")
   
	async def player(message, inst, args):
		user_id = message.author.id
		admin_check = await inst.checkAdmin(user_id)
		if not admin_check:
				return
		await inst.matchmake()
		
	async def unscheduledGame(message, inst, args):
		user_id = message.author.id
		admin_check = await inst.checkAdmin(user_id)
		if not admin_check:
			return
		await inst.unscheduledGames(args, message.channel)
  
	async def rank(message, inst, args):
		await inst.displayRank(message)

	# Make Admin Command
	async def leaderboard(message, inst, args):
		await inst.displayLeaderboard(message.channel)
  
	# Make Admin Command
	async def endmatch(message, inst, args):
		await inst.endMatch(message, args[0])
  
	# Punsih player
	async def punish(message, inst, args):
		await inst.punishPlayer(message, args[0])
  
	# Ask for Swap
	async def swap(message, inst, args):
		await inst.swapPlayers(message, args[0])
  
	# Check if admin
	async def isAdmin(message, inst, args):
		await inst.checkAdmin(message.author.id)
  
	# Replaces One player for another
	async def replace(message, inst, args):
		await inst.replacePlayer(message, args[0], args[1])

	async def roles(message, inst, args):
		await inst.roles(message)

	async def win(message, inst, args):
		await inst.win(message)
  
	async def mmtest(message, inst, args):
		current_matches = []
		player_list = [197057417358475264, 199549110187982848, 197058147167371265, 127796716408799232, 180398163620790279, 225650967058710529, 618520923204485121, 160471312517562368, 188370105413926912, 694560846814117999]
		matches = await inst.matchmakeV2(player_list)
		current_matches.extend(matches)
		match_string = str(matches).replace("[", "")
		match_string = match_string.replace("]", "")
		msg = await message.channel.send(match_string)
		await msg.edit(suppress=True)

		
	async def help(message, inst, args):
		txt = "```List of commands:\n"
		for command in commands.userCommands:
			txt += f"!{command}\n" #and a description
		await message.channel.send(txt + "```")

	userCommands = {
		'hello' : hello,
		'queue' : queue,
		'dequeue' : dequeue,
		'signup' : signup,
		'add-acc': addAccount,
		'player': player,
		'unscheduledgame' : unscheduledGame,
		'rank': rank,
		'leaderboard': leaderboard,
		'end-match': endmatch,
		'punish': punish,
		'swap': swap,
		'win' : win,
		'admin': isAdmin,
		'replace': replace,
		'roles': roles,
		'help' :help,
		'mmtest': mmtest
		}

	async def parseReaction(reaction, inst):
		# Change Player Role
		await inst.changePlayerRole(reaction)
  
  
	async def parse(message, inst):
		client = inst.client
		if message.author == client.user or not message.content.startswith(commands.COMMAND_SYMBOL):
			return
		text = message.content.split(" ")
		command = (text[0][1:]).lower()
		args = text[1:]
		try:
			await commands.userCommands[command](message, inst, args)
		except KeyError:
			await message.channel.send(f"Command not recognised.\nUse !help to see a list of commands")


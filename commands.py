
from player import Player
from team import Team
from match import Match

class commands:
	COMMAND_SYMBOL = "!"
	
	async def hello(message, inst, args):
		print("working")
		await message.channel.send("hiya")

	async def queue(message, inst, args):
		await inst.addToQueue(message.author, message.channel)

	async def dequeue(message, inst, args):
		await inst.removeFromQueue(message.author, message.channel)

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
		await inst.matchmake()
		
	async def unscheduledGame(message, inst, args):
		await inst.unscheduledGames(args, message.channel)
  
	async def rank(message, inst, args):
		await inst.displayRank(message)

	# Make Admin Command
	async def leaderboard(message, inst, args):
		await inst.displayLeaderboard(message)
  
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
		inst.win(message)
		pass

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
		'roles': roles
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
			await message.channel.send(f"Command '{command}' not recognised")


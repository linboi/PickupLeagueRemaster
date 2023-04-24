
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
  
		# Give access to '#select-roles' channel
		if(signUpSuccess):
			await message.channel.send(pName + " (" + pRank + ")")
		else:
			await message.channel.send(pName + " (" + pRank + ")")
			await message.channel.send("Failed 😔 please try again!")
   
	async def addAccount(message, inst, args):
		pRank, pName, signUpSuccess = await inst.addAccount(args[0], message)
		if signUpSuccess:
			await message.channel.send("🗃️ Account Added: " + pName)
		else:
			await message.channel.send(pName + " (" + pRank + ")")
   
	async def player(message, inst, args):
		test = await inst.createPlayerObject(24)
		test.addWin()
		test.update()
		
	async def unscheduledGame(message, inst, args):
		await inst.unscheduledGames(args, message.channel)
		await inst.matchmake()
  
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
		'swap': swap
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


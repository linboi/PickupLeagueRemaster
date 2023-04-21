

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
		pRank, pName = await inst.opggWebScrape(args[0], message.author)
		# Give access to '#select-roles' channel
		await message.channel.send(pName + " (" + pRank + ")" + "\n" + str(message.author.id))

	userCommands = {
		'hello' : hello,
		'queue' : queue,
		'dequeue' : dequeue,
		'signup' : signup
		}

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


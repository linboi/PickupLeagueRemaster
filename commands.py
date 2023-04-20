

class commands:
	COMMAND_SYMBOL = "!"
	
	async def hello(message, inst, args):
		print("working")
		await message.channel.send("hiya")

	async def queue(message, inst, args):
		await inst.addToQueue(message.author, message.channel)

	async def dequeue(message, inst, args):
		await inst.removeFromQueue(message.author, message.channel)

	userCommands = {
		'hello' : hello,
		'queue' : queue,
		'dequeue' : dequeue
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
		except:
			await message.channel.send(f"Command '{command}' not recognised")


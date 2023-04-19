class commands:
	
	async def parse(message, client, inst):
		if message.author == client.user:
			return

		if message.content.startswith('$hello'):
			await message.channel.send('Hello!')

		if message.content.startswith('$queue'):
			await inst.addToQueue(message.author, message.channel)

		if message.content.startswith('$dequeue'):
			await inst.addToQueue(message.author, message.channel)

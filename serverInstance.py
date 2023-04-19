class serverInstance:
	def __init__(self):
		self.queue = []

	def ready(self, client, announcementChannel):
		self.client = client
		self.announcementChannel = announcementChannel
	
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
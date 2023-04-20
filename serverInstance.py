import requests
from bs4 import BeautifulSoup

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
	
	# Scrape rank details from op.gg page
	async def opggWebScrape(self, msg_content, discord_id):
	
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
	
		# Try scraping valid OP.GG URL - Rank, Summoner Name.
		try:
			rank = doc.find_all(class_="tier")
			rank = rank[0].decode_contents().strip()
			rank = rank.replace("<!-- -->", "")
			rank = rank.split()
			rank_str = ""
			for char in rank:
				rank_str += char[0]
	
			summoner_name = doc.find_all(class_="summoner-name")
			summoner_name = summoner_name[0].decode_contents().strip()
	
			# Insert into DB - discord ID✅, Name✅, Rank✅
			# Give access to #select-role text channel
	
		except:
			rank_str = "Invalid Account"
			summoner_name = "Invalid Account"
	
	
		return rank_str.upper(), summoner_name
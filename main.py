import discord
import json
from riotwatcher import LolWatcher, ApiError

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

api_token = "RGAPI-d83ff2d7-9bd7-4edb-99fc-beb4cdbb7a2b"
lol_watcher = LolWatcher(api_token)
region = 'EUW1'

@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')

	if message.content.startswith('$rank'):
		words = message.content.split(" ")
		summoner_info = lol_watcher.summoner.by_name(region, words[1])
		my_ranked_stats = lol_watcher.league.by_summoner(region, summoner_info['id'])
		await message.channel.send(repr(my_ranked_stats))
		print(summoner_info)

def main():
	with open('./secret.json') as f:
	
		secret = json.load(f)
				
	with open('./settings.json') as f:
	
		settings = json.load(f)

	client.run(secret['BOT_TOKEN'])
		
if __name__ == '__main__':
	main()
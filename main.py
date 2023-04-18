import discord
import json


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    

    if message.content.startswith('$hello'):
        await message.channel.send('Fionn is a dog 🐶!')
        
    if message.content.startswith('$fetch'):
        await message.channel.send('Exit')
        
        

def main():
	with open('./secret.json') as f:
	
		secret = json.load(f)
                
	with open('./settings.json') as f:
	
		settings = json.load(f)

	client.run(secret['BOT_TOKEN'])
 
	
        
if __name__ == '__main__':
	main()
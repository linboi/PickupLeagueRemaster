import discord
import json
import mariadb

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
        
        
def connectPlayerDatabase(message):
    # Connect to MariaDB Platform
	try:
		conn = mariadb.connect(
			user="root",
			password="cailean",
			host="127.0.0.1",
			port=3306,
			database="league-test"
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()
	return cur

def main():
	with open('./secret.json') as f:
	
		secret = json.load(f)
                
	with open('./settings.json') as f:
	
		settings = json.load(f)

	client.run(secret['BOT_TOKEN'])
	connectPlayerDatabase()
 
	
        
if __name__ == '__main__':
	main()

from player import Player
from team import Team
from match import Match
import re

class commands:
    COMMAND_SYMBOL = "!"
    
    async def hello(message, inst, args):
        print("working")
        await message.channel.send("hiya")

    async def queue(message, inst, args):
        state = inst.getQueueState()
        if state:
            await inst.addToQueue(message.author.id, message.channel)

    async def dequeue(message, inst, args):
        await inst.removeFromQueue(message.author.id, message.channel)
  
    async def switchQueueState(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
                return

        state = await inst.queueSwitch()
        if state == False:
            await message.channel.send("Queue is disabled, and list emptied.")
        else:
            await message.channel.send("Queue is enabled")

    async def signup(message, inst, args):
        pRank, pName, signUpSuccess = await inst.signUpPlayer(args[0], message)
        print(pRank)
        print(pName)
        # Give access to '#select-roles' channel
        if(signUpSuccess == False):
            await message.channel.send("Failed 😔 please try again!")
        if(signUpSuccess == True):
            await inst.applyRole(message)
   
    async def addAccount(message, inst, args):
        pRank, pName, signUpSuccess = await inst.addAccount(args[0], message)
  
        if signUpSuccess:
            await message.channel.send("🗃️ Account Added: " + pName)
        else:
            await message.channel.send(pName + " (" + pRank + ")")
   
    async def player(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
                return
        await inst.matchmake()
        
    async def unscheduledGame(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            return
        await inst.unscheduledGames(args)
  
    async def rank(message, inst, args):
        await inst.displayRank(message)

    # Make Admin Command
    async def leaderboard(message, inst, args):
        await inst.displayLeaderboard(message.channel)

    async def bettyboard(message, inst, args):
        await inst.displayBettyBoard(message.channel)
  
    # Make Admin Command
    async def endmatch(message, inst, args):
        await inst.endMatch(message, args[0])

    async def runSQL(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            return
        await inst.runSQL(message, args)
  
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
        await inst.win(message)
  
    async def testTag(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            return
        await inst.testTag(message)
  
    # Resolve match with matchid and side as input ('RED', 'BLUE')
    async def adminWin(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            return
        await inst.adminWin(message, args[0], args[1])
  
    # Test function for mm troubleshooting
    async def matchmakingtest(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            return
        await inst.mmTest()
  
    async def customMatch(message, inst, args):
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
                return
        id_list = []
        for arg in args:
            arg_int = re.sub(r'[a-z<>@]', '', arg)
            arg_int = arg_int.strip()
            if arg_int != '':
                id_list.append(arg_int)
        idint_list = [int(i) for i in id_list]
        if len(idint_list) == 10: 
            try:
                await inst.createCustomMatch(idint_list)
                await message.channel.send("✅ Match Created")
            except:
                await message.channel.send("Match Creation Error, please make all players are valid discord @'s.")
        else:
            await message.channel.send(f"You need **10** players, you had *{len(idint_list)}*.")
          
    async def help(message, inst, args):
        txt = "```List of commands:\n"
        for command in commands.userCommands:
            txt += f"!{command}\n" #and a description
        await message.channel.send(txt + "```")

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
        'lb': leaderboard,
        'bettyboard': bettyboard,
        'bb': bettyboard,
        'end-match': endmatch,
        'punish': punish,
        'swap': swap,
        'win' : win,
        'admin': isAdmin,
        'replace': replace,
        'roles': roles,
        'help' :help,
        'resolve-match': adminWin,
        'queue-switch': switchQueueState,
        'matchmaketest': matchmakingtest,
        'custom-match': customMatch,
        'test': testTag,
        'runsql':runSQL
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
            await message.channel.send(f"Command not recognised.\nUse !help to see a list of commands")

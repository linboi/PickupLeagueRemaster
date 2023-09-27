from rasp import rasp
import discord
import re
import os
from logger import Logger

#setup logger
logger = Logger().logger

class commands:
    COMMAND_SYMBOL = "!"

    async def hello(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        try:
            logger.info(f"User: {message.author.id} | Bot Working")
            await message.channel.send("hiya")
        except Exception as e:
            logger.error(e)


    async def queue(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        state = inst.getQueueState()
        logger.info(f"Queue State: {state}")
        if state:
            logger.info(f"attempting to add {message.author.id} to queue")
            await inst.addToQueue(message.author.id, message.channel)

    async def dequeue(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        logger.info(f"attempting to remove {message.author.id} from queue")
        await inst.removeFromQueue(message.author.id, message.channel)

    async def switchQueueState(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return

        state = await inst.queueSwitch()
        if state == False:
            await message.channel.send("Queue is disabled, and list emptied.")
            logger.info(f"Queue is disabled, and list emptied.")
        else:
            await message.channel.send("Queue is enabled")
            logger.info(f"Queue is enabled")

    async def signup(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        try:
            pRank, pName, signUpSuccess = await inst.signUpPlayer(args[0], message)
        except Exception as e:
            signUpSuccess = False
            logger.error(e)
        finally:
            #print(pRank)
            #print(pName)
            # Give access to '#select-roles' channel
            if (signUpSuccess == False):
                await message.channel.send("Failed 😔 please try again!")
                logger.warning(f"Sign up failed for {message.author.id}")
            await inst.applyRole(message)

    async def addAccount(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        pRank, pName, signUpSuccess = await inst.addAccount(args[0], message)

        if signUpSuccess:
            await message.channel.send("🗃️ Account Added: " + pName)
            logger.info(f"User: {message.author.id} | Account Added: {pName}")
        else:
            await message.channel.send(pName + " (" + pRank + ")")

    async def player(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        await inst.matchmake()

    async def unscheduledGame(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        if args[0].lower() == "aram":
            await inst.unscheduledGames(args[1:], mode="aram")
        else:
            await inst.unscheduledGames(args)

    async def rank(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.displayRank(message)

    # Make Admin Command
    async def leaderboard(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        if len(args) == 0:
            await inst.displayLeaderboard(message.channel)
        else:
            await inst.displayLeaderboard(message.channel, mode=args[0].lower())

    async def bettyboard(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.displayBettyBoard(message.channel)

    # Make Admin Command
    async def endmatch(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.endMatch(message, args[0])

    async def runSQL(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        await inst.runSQL(message, args)

    # Punsih player
    async def punish(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.punishPlayer(message, args[0])

    # Ask for Swap
    async def swap(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.swapPlayers(message, args[0])

    # Check if admin
    async def isAdmin(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.checkAdmin(message.author.id)

    # Replaces One player for another
    async def replace(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.replacePlayer(message, args[0], args[1])

    async def roles(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.roles(message)

    async def win(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        try:
            gameID = int(args[0])
            logger.info(f"User: {message.author.id} | WON | GameID: {gameID}")
        except Exception as e:
            await message.channel.send("Please include the gameID found at the top of the match summary screen.\nIf this is unavailable for some reason, use 0.")
            logger.error(f"User: {message.author.id} | Suspected gameID not found | {e}")
        else:
            await inst.win(message, gameID)

    async def testTag(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        await inst.testTag(message)

    # Resolve match with matchid and side as input ('RED', 'BLUE')
    async def adminWin(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        await inst.adminWin(message, args[0], args[1])

    # Test function for mm troubleshooting
    async def matchmakingtest(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        if len(args) > 0 and args[0].lower() == "aram":
            await inst.mmTest(mode="aram")
        else:
            await inst.mmTest()

    async def customMatch(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
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
            except Exception as e:
                await message.channel.send("Match Creation Error, please make all players are valid discord @'s.")
                logger.error(f"User: {message.author.id} | Match Creation Error | {e}")
        else:
            await message.channel.send(f"You need **10** players, you had *{len(idint_list)}*.")

    async def help(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        txt = "```List of commands:\n"
        for command in commands.userCommands:
            txt += f"!{command}\n"  # and a description
        await message.channel.send(txt + "```")

    async def setMatch(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        await inst.setMatch(message)

    async def update(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        await inst.updatePlayerMMRs(message)

    async def rasp_update(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        output = rasp.update_pi()
        await message.channel.send(f"```{output}```")

    async def rasp_reboot(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        user_id = message.author.id
        admin_check = await inst.checkAdmin(user_id)
        if not admin_check:
            logger.warning(f"User: {message.author.id} |  User is not an admin")
            return
        rasp.restart_pi()

    async def rasp_upload(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        if not await inst.checkAdmin(message.author.id):
            return
        await inst.upload_db(message.author)

    async def history(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        if len(message.mentions) > 0:
            await inst.displayHistory(message.mentions[0], message)
        else:
            await inst.displayHistory(message.author, message)

    async def history_with(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        if len(message.mentions) > 0:
            await inst.displayHistoryWith(message.mentions[0], message)
        else:
            await message.channel.send("Please choose a player to check your history with")

    async def profile(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        if len(message.mentions) > 0:
            await inst.showProfile(message.mentions[0], message)
        else:
            await inst.showProfile(message.author, message)

    async def updatePUUIDs(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.updatePUUIDs(message.channel)

    async def getGameDetails(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.getGameDetails(message.channel)

    async def updatePlayerMatchDetails(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.updatePlayerMatchDetails(message.channel, args[0])

    async def updateAPIKey(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.updateAPIKey(message, args[0])

    async def mainAccount(message, inst, args):
        logger.info(f"User: {message.author.id} | Command: {message.content}")
        await inst.updateMainAccount(message)

    userCommands = {
        'hello': hello,
        'queue': queue,
        'dequeue': dequeue,
        'signup': signup,
        'add-acc': addAccount,
        'player': player,
        'unscheduledgame': unscheduledGame,
        'rank': rank,
        'leaderboard': leaderboard,
        'lb': leaderboard,
        'bettyboard': bettyboard,
        'bb': bettyboard,
        'end-match': endmatch,
        'punish': punish,
        'swap': swap,
        'win': win,
        'admin': isAdmin,
        'replace': replace,
        'roles': roles,
        'help': help,
        'resolve-match': adminWin,
        'queue-switch': switchQueueState,
        'matchmaketest': matchmakingtest,
        'custom-match': customMatch,
        'set-match': setMatch,
        'test': testTag,
        'runsql': runSQL,
        'update': update,
        'fetch-db': rasp_upload,
        'git-pull': rasp_update,
        'restart-pi': rasp_reboot,
        'history': history,
        'history-with': history_with,
        'update-puuids': updatePUUIDs,
        'get-game-details': getGameDetails,
        'update-player-match-details': updatePlayerMatchDetails,
        'profile': profile,
        'update-api-key': updateAPIKey,
        'mainaccount': mainAccount
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

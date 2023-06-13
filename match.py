from player import Player
from team import Team
import random
import copy
import datetime
import asyncio
import time


class Match:
    def __init__(self, cursor, con, client, matchID=None, blueTeam=None, redTeam=None, startTime='TODAY'):

        self.matchID = matchID
        self.blueTeam = blueTeam
        self.redTeam = redTeam
        self.startTime = startTime
        self.cursor = cursor
        self.con = con
        self.blueBets = {}
        self.redBets = {}
        self.client = client
        self.tournament_code = None

    def __repr__(self):
        return self.get_details_string()

    def set_red(self, team):
        self.redTeam = team

    def set_blue(self, team):
        self.blueTeam = team

    def set_matchID(self, id):
        self.matchID = id

    def get_matchID(self):
        return self.matchID

    def get_red(self):
        return self.redTeam

    def get_blue(self):
        return self.blueTeam

    def get_tournament_code(self):
        return self.tournament_code

    def set_tournament_code(self, code):
        self.tournament_code = code

    # MMR Difference Between Both Teams
    def calculateMMRDifference(self, teamR, teamB):
        # Get the AVG MMR of both teams
        btMMR = teamB.get_avg_MMR()
        rtMMR = teamR.get_avg_MMR()
        # Get the MMR Difference between init teams
        mmrDifference = abs(rtMMR - btMMR)
        return mmrDifference

    # Return the details of the current match in string
    def get_details_string(self):
        discordIDs = ", ".join(str(p.get_dID()) for p in self.blueTeam.get_player_list(
        ) + self.redTeam.get_player_list())
        res = self.cursor.execute(
            f"SELECT [name] FROM Account JOIN Player ON Account.playerID = Player.playerID WHERE Player.discordID in ({discordIDs})").fetchall()
        invite_strings = []
        idx = 0
        while idx < len(res):
            invite_string = ",".join(
                str(name[0]) for name in res[idx:min(len(res)-1, idx+10)])
            invite_strings.append(invite_string)
            idx += 10
        string = f"   \n✨ MatchID ({self.matchID})\t\t🏅 MMR Difference ({round(self.calculateMMRDifference(self.blueTeam, self.redTeam))})"
        string += f"\n```{'[Blue Team]': ^15}{'':^5}{'[Red Team]':^15}\n\n"
        string += f"{self.blueTeam.get_top().get_username():^15}{'(top)':^5}{self.redTeam.get_top().get_username():^15}\n"
        string += f"{self.blueTeam.get_jg().get_username():^15}{'(jng)':^5}{self.redTeam.get_jg().get_username():^15}\n"
        string += f"{self.blueTeam.get_mid().get_username():^15}{'(mid)':^5}{self.redTeam.get_mid().get_username():^15}\n"
        string += f"{self.blueTeam.get_adc().get_username():^15}{'(adc)':^5}{self.redTeam.get_adc().get_username():^15}\n"
        string += f"{self.blueTeam.get_sup().get_username():^15}{'(sup)':^5}{self.redTeam.get_sup().get_username():^15}\n```"
        string += f"{self.tournament_code}"
        for i, invite_string in enumerate(invite_strings):
            string += f"\nInvite list{i}: {invite_string}"

        return string

    # Return OPGG Link of Hightest Account per Player()
    def getOPGGLink(self):
        blue_link = self.blueTeam.get_multi_opgg()
        red_link = self.redTeam.get_multi_opgg()
        return blue_link, red_link

    async def replacePlayer(self, discordID, otherID, channel, client):
        listOfPlayers = [self.redTeam.get_player_list() +
                         self.blueTeam.get_player_list()]
        discordID = int(discordID)
        otherID = int(otherID)
        player_found = False
        # [player(), "red or blue", "jng"]
        team = []
        res = self.cursor.execute(
            f"SELECT * FROM Player WHERE discordID = {otherID}")
        player_details = res.fetchone()
        try:
            discordUser = await client.fetch_user(player_details[1])
        except:
            discordUser = None
        replacement_player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                            player_details[9], player_details[10], player_details[11], player_details[12], player_details[13], player_details[14], player_details[15], self.cursor, self.con, discordUser)

        # Check if player exists in Game
        for player in listOfPlayers:
            for user in player:

                if (user.get_dID() == discordID):
                    # If the player does exist, what team?
                    # Red Team
                    for player in self.redTeam.get_player_list():
                        if player.get_dID() == discordID:
                            team.append(player)
                            team.append('red')
                            team.append(player.get_role().lower())
                            if team[2] == 'top':
                                self.redTeam.set_top(replacement_player)
                            elif team[2] == 'jng':
                                self.redTeam.set_jg(replacement_player)
                            elif team[2] == 'mid':
                                self.redTeam.set_mid(replacement_player)
                            elif team[2] == 'adc':
                                self.redTeam.set_adc(replacement_player)
                            elif team[2] == 'sup':
                                self.redTeam.set_sup(replacement_player)

                    # Blue Team
                    for player in self.blueTeam.get_player_list():
                        if player.get_dID() == discordID:
                            team.append(player)
                            team.append('blue')
                            team.append(player.get_role().lower())
                            if team[2] == 'top':
                                self.blueTeam.set_top(replacement_player)
                            elif team[2] == 'jng':
                                self.blueTeam.set_jg(replacement_player)
                            elif team[2] == 'mid':
                                self.blueTeam.set_mid(replacement_player)
                            elif team[2] == 'adc':
                                self.blueTeam.set_adc(replacement_player)
                            elif team[2] == 'sup':
                                self.blueTeam.set_sup(replacement_player)

                    new_details = self.get_details_string()
                    await channel.send(f"{new_details}")
                    player_found = True
                else:
                    pass

        return player_found

    # Swap two players in a Match

    async def swapPlayers(self, discordID, otherID, message_obj):
        listOfPlayers = [self.redTeam.get_player_list() +
                         self.blueTeam.get_player_list()]
        discordID = int(discordID)
        otherID = int(otherID)
        blueFound = False
        redFound = False
        # [player(), "red or blue", "jng"]
        team = []
        other_team = []

        # Check if player exists in Game
        for player in listOfPlayers:
            for user in player:

                if (user.get_dID() == discordID or user.get_dID() == otherID):
                    # If the player does exist, what team?
                    # Red Team
                    for player in self.redTeam.get_player_list():
                        if player.get_dID() == discordID:
                            team.append(player)
                            team.append('red')
                            team.append(player.get_role())
                            redFound = True
                        elif player.get_dID() == otherID:
                            other_team.append(player)
                            other_team.append('red')
                            other_team.append(player.get_role())
                            blueFound = True

                    # Blue Team
                    for player in self.blueTeam.get_player_list():
                        if player.get_dID() == discordID:
                            team.append(player)
                            team.append('blue')
                            team.append(player.get_role())
                            redFound = True
                        elif player.get_dID() == otherID:
                            other_team.append(player)
                            other_team.append('blue')
                            other_team.append(player.get_role())
                            blueFound = True

        # If both players found -> replace player
        if blueFound or redFound:
            # Swap roles
            team[0].set_role(other_team[2])
            other_team[0].set_role(team[2])

            # Swap role of original player
            if team[1] == 'red':
                if other_team[2] == 'top':
                    self.blueTeam.set_top(team[0])
                elif other_team[2] == 'jng':
                    self.blueTeam.set_jg(team[0])
                elif other_team[2] == 'mid':
                    self.blueTeam.set_mid(team[0])
                elif other_team[2] == 'adc':
                    self.blueTeam.set_adc(team[0])
                elif other_team[2] == 'sup':
                    self.blueTeam.set_sup(team[0])
            elif team[1] == 'blue':
                if other_team[2] == 'top':
                    self.redTeam.set_top(team[0])
                elif other_team[2] == 'jng':
                    self.redTeam.set_jg(team[0])
                elif other_team[2] == 'mid':
                    self.redTeam.set_mid(team[0])
                elif other_team[2] == 'adc':
                    self.redTeam.set_adc(team[0])
                elif other_team[2] == 'sup':
                    self.redTeam.set_sup(team[0])

            # Swap role of other player
            if other_team[1] == 'red':
                if team[2] == 'top':
                    self.blueTeam.set_top(other_team[0])
                elif team[2] == 'jng':
                    self.blueTeam.set_jg(other_team[0])
                elif team[2] == 'mid':
                    self.blueTeam.set_mid(other_team[0])
                elif team[2] == 'adc':
                    self.blueTeam.set_adc(other_team[0])
                elif team[2] == 'sup':
                    self.blueTeam.set_sup(other_team[0])
            elif other_team[1] == 'blue':
                if team[2] == 'top':
                    self.redTeam.set_top(other_team[0])
                elif team[2] == 'jng':
                    self.redTeam.set_jg(other_team[0])
                elif team[2] == 'mid':
                    self.redTeam.set_mid(other_team[0])
                elif team[2] == 'adc':
                    self.redTeam.set_adc(other_team[0])
                elif team[2] == 'sup':
                    self.redTeam.set_sup(other_team[0])

            # self.findFairestTeams()
            new_details = self.get_details_string()
            await message_obj.channel.send(f"{new_details}")
            print("done")
        else:
            pass

    # Delete Match from DB
    def delete(self):
        self.cursor.execute(
            f"DELETE FROM Match WHERE matchID = {self.matchID}")
        self.con.commit()

    # Return list of Players on both team
    def listOfUsers(self):
        listOfPlayers = [self.redTeam.get_player_list() +
                         self.blueTeam.get_player_list()]
        listOfUsers = []
        for player in listOfPlayers:
            for user in player:
                listOfUsers.append(user.get_dID())
        return listOfUsers

    def resolve(self, winner, gameID):
        if winner == 'BLUE':
            winningTeam = self.blueTeam
            losingTeam = self.redTeam
            self.resolveBets(self.blueBets, self.redBets)
        elif winner == 'RED':
            winningTeam = self.redTeam
            losingTeam = self.blueTeam
            self.resolveBets(self.redBets, self.blueBets)

        MMRdiff = losingTeam.get_avg_MMR() - winningTeam.get_avg_MMR()
        expectedScore = 1/(1 + 10**(MMRdiff/500))

        kValue = 100
        ratingChange = kValue * (1-expectedScore)

        for player in winningTeam.get_player_list():
            player.fetchPlayerDB()
            player.addWin()
            player.updateRating(ratingChange)
            player.updateLP(ratingChange)
            player.update()

        for player in losingTeam.get_player_list():
            player.fetchPlayerDB()
            player.addLoss()
            player.updateRating(-ratingChange)
            player.updateLP(-ratingChange)
            player.update()
        self.update(ratingChange, winningTeam, losingTeam, winner, gameID)
        return ratingChange

    def update(self, ratingchange, winningTeam, losingTeam, winner, gameID):
        if winner != 'BLUE':
            loser = 'BLUE'
        else:
            loser = 'RED'
        self.cursor.execute(
            f"UPDATE Match SET resolutionTime = '{datetime.datetime.now()}', gameID = {gameID} WHERE matchID = {self.matchID}")
        for p in winningTeam.get_player_list():
            self.cursor.execute(f"""INSERT INTO PlayerMatch (playerID, matchID, ratingChange, [role], team)
                                    VALUES ({p.get_pID()}, {self.matchID}, {ratingchange}, '{p.get_role()}', '{winner}')""")
        for p in losingTeam.get_player_list():
            self.cursor.execute(f"""INSERT INTO PlayerMatch (playerID, matchID, ratingChange, [role], team)
                                    VALUES ({p.get_pID()}, {self.matchID}, {-ratingchange}, '{p.get_role()}', '{loser}')""")
        self.con.commit()

    def resolveBets(self, winners, losers):
        totalPool = 0
        winnerPool = 0
        for key in winners:
            totalPool += winners[key]
            winnerPool += winners[key]
        for key in losers:
            totalPool += losers[key]
        for key in winners:
            winnings = (winners[key]/winnerPool)*totalPool
            self.cursor.execute(f"""
                UPDATE Player 
                SET bettingPoints = bettingPoints + {winnings}
                WHERE discordID = {key}
            """)
            self.con.commit()

    async def openBetting(self, message):
        await message.add_reaction('🔵')
        await message.add_reaction('🔴')
        closingTime = datetime.datetime.now() + datetime.timedelta(minutes=11)
        matchMessage = message.content
        await message.edit(content=(matchMessage + "\nBetting closes:<t:" + str(int(time.mktime(closingTime.timetuple()))) + ":R>"))

        def check(reaction, user):
            return (reaction.message.id == message.id and reaction.emoji in ['🔴', '🔵'])

        bettingClosed = False

        while not bettingClosed:
            try:
                team, user = await self.client.wait_for('reaction_add', check=check, timeout=(closingTime - datetime.datetime.now()).total_seconds())
                teamChosen = ""
                if team.emoji == '🔵':
                    teamChosen = "BLUE"
                if team.emoji == '🔴':
                    teamChosen = "RED"
                asyncio.create_task(self.respondToBet(
                    user, teamChosen, closingTime))
            except asyncio.TimeoutError:
                bettingClosed = True
        await message.clear_reactions()

    async def respondToBet(self, user, team, closingTime):
        if team == "":
            print("this code should be unreachable")
            return
        if team == "BLUE":
            for player in self.redTeam.get_player_list():
                if player.get_dID() == user.id:
                    await user.send("You can't bet against yourself.")
                    return
        if team == "RED":
            for player in self.blueTeam.get_player_list():
                if player.get_dID() == user.id:
                    await user.send("You can't bet against yourself.")
                    return
        res = self.con.execute(
            f"SELECT bettingPoints FROM Player WHERE discordID = {user.id}")
        # I know the comma looks weird here, python syntax for turning a single element tuple into that element is strange
        balance, = res.fetchone()

        await user.send(f"How much do you want to bet on team {team} in match {self.matchID} (current balance: {balance:.0f}):")

        def check(message):
            return message.author.id == user.id and int(message.content) > 0
        try:
            msg = await self.client.wait_for('message', check=check, timeout=(closingTime - datetime.datetime.now()).total_seconds())
        except asyncio.TimeoutError:
            await user.send("Out of time.")
            return
        amount = int(msg.content)
        res = self.con.execute(
            f"SELECT bettingPoints FROM Player WHERE discordID = {user.id}")
        # after any awaits we have to check that the user still has enough to make the bet
        balance, = res.fetchone()
        # basically from here to committing the bet is a critical section, no awaits allowed
        if balance < amount:
            # except here because we're not committing the bet
            await user.send("Insufficient balance")
            return
        res = self.con.execute(
            f"UPDATE Player SET bettingPoints = bettingPoints-{amount} WHERE discordID = {user.id}")
        if res.rowcount != 1:
            print("Bet failed")
            return
        if team == "BLUE":
            if user.id in self.blueBets:
                self.blueBets[user.id] += amount
            else:
                self.blueBets[user.id] = amount
        else:
            if user.id in self.redBets:
                self.redBets[user.id] += amount
            else:
                self.redBets[user.id] = amount
        await user.send(f"Successfully placed a bet of {amount:.0f} on team {team} in match {self.matchID}!")

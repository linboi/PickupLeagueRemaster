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
        
    def __repr__(self):
        string = f"   \n✨ **MatchID** (*{self.matchID}*)\t \t⏲️ **Match Time** (*{self.startTime}*)\t \t 🏅 **MMR Difference** (*{round(self.calculateMMRDifference(self.blueTeam, self.redTeam))}*)"
        string += f"\n```{'[Blue Team]': ^15}{'':^5}{'[Red Team]':^15}\n\n"
        string += f"{self.blueTeam.get_top().get_username():^15}{'(top)':^5}{self.redTeam.get_top().get_username():^15}\n"
        string += f"{self.blueTeam.get_jg().get_username():^15}{'(jng)':^5}{self.redTeam.get_jg().get_username():^15}\n"
        string += f"{self.blueTeam.get_mid().get_username():^15}{'(mid)':^5}{self.redTeam.get_mid().get_username():^15}\n"
        string += f"{self.blueTeam.get_adc().get_username():^15}{'(adc)':^5}{self.redTeam.get_adc().get_username():^15}\n"
        string += f"{self.blueTeam.get_sup().get_username():^15}{'(sup)':^5}{self.redTeam.get_sup().get_username():^15}\n```"
        opgg_red , opgg_blue = self.getOPGGLink()
        string += f"\n **🔵 Blue Team OPGG:** {opgg_red}\n **🔴 Red Team OPGG:** {opgg_blue}"
        return string
        
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
    
    
    # Primary fn() for Matchmaking
    def assignRoles(self, playerList):
        
        # Shuffle & Order Player for PQ Value
        sortedPlayers = self.shuffle_orderPQ(playerList)
        # Select first 10 players & Sort into roles
        sortRoles = self.fitRoles(sortedPlayers[:10])
        # Add PQ to players who missed out
        
        # Set init roles for each team
        self.setInitTeams(sortRoles)
        # Shuffle teams to find fairest
        team1, team2 = self.findFairestTeams()
        # Create a new teams w/ fair combinations
        self.setFairTeams(team1, team2)
        
    # Order players based on QP
    def shuffle_orderPQ(self, playerList, reqPLayers):
        
        # Add signup, set QP in DB
        for player in playerList:
            # Incremenets signupCount & Updates QP Value
            player.addSignUpCount()
 
        # Shuffle the player list
        random.shuffle(playerList)
        # Use the sorted function to order the list in terms of QP value ASC
        ordered_pq_list = sorted(playerList, key=lambda p: p.get_QP())
        # All players left out recieve a +1 PQ Value
        for player in ordered_pq_list[reqPLayers:]:
            print(f"Player Left Out: {player.get_pID()}[{player.get_QP()}]\n")
            player.addGameMissed()
        # Return Final List
        return ordered_pq_list[:reqPLayers]
    
    # Ordered list based on MMR
    def orderBasedOnMMR(self, selectedPlayerList):
        # Order selected players on MMR
        ordered_rank_list = sorted(selectedPlayerList, key=lambda p: p.get_rating(), reverse=True)
        return ordered_rank_list
        
    # For a set of Players assign roles based on Role Preferences
    def fitRoles(self, players):
        
        # Array for filled players
        fill_players = []
        
        # Init an empty dictionary of roles
        assigned_roles = {
            'top':[],
            'jng':[],
            'mid':[],
            'adc':[],
            'sup':[]
        }
        
        # Loop & Set assigned role. NEED TO ADD SET_TEMPMMR() FOR FILL PLAYERS
        for player in players:
            if len(assigned_roles['top']) < 2 and player.get_pRole() == 'TOP':
                assigned_roles['top'].append(player)
                player.set_role('top')
            elif len(assigned_roles['jng']) < 2 and player.get_pRole() == 'JNG':
                assigned_roles['jng'].append(player)
                player.set_role('jng')
                
            elif len(assigned_roles['mid']) < 2 and player.get_pRole() == 'MID':
                assigned_roles['mid'].append(player)
                player.set_role('mid')
                
            elif len(assigned_roles['adc']) < 2 and player.get_pRole() == 'ADC':
                assigned_roles['adc'].append(player)
                player.set_role('adc')
                
            elif len(assigned_roles['sup']) < 2 and player.get_pRole() == 'SUP':
                assigned_roles['sup'].append(player)
                player.set_role('sup')
                
            elif player.get_pRole() == 'FILL':
                fill_players.append(player)
                
            elif len(assigned_roles['top']) < 2 and player.get_sRole() == 'TOP':
                assigned_roles['top'].append(player)
                player.set_role('top')
                
            elif len(assigned_roles['jng']) < 2 and player.get_sRole() == 'JNG':
                assigned_roles['jng'].append(player)
                player.set_role('jng')
                
            elif len(assigned_roles['mid']) < 2 and player.get_sRole() == 'MID':
                assigned_roles['mid'].append(player)
                player.set_role('mid')
                
            elif len(assigned_roles['adc']) < 2 and player.get_sRole() == 'ADC':
                assigned_roles['adc'].append(player)
                player.set_role('adc')
                
            elif len(assigned_roles['sup']) < 2 and player.get_sRole() == 'SUP':
                assigned_roles['sup'].append(player)
                player.set_role('sup')
                
            elif player.get_sRole() == 'FILL':
                fill_players.append(player)
                
            else:
                # If player pRole & sRole is taken, add to FILL
                fill_players.append(player)
        
        # Shuffle Fill
        random.shuffle(fill_players)
        
        # For each player in FILL, assign the remaining roles in a RANDOM order
        for player in fill_players:
            available_roles = [role for role in assigned_roles.keys() if len(assigned_roles[role]) < 2]
            if available_roles:
                role = random.choice(available_roles)
                # Set MMR reduction

                assigned_roles[role].append(player)
                # Set assigned role for game
                player.set_role(role)
        
                
        return assigned_roles
    
    # Set initial roles for each team
    def setInitTeams(self, players):
        
        redTeam = Team()
        blueTeam = Team()
        
        redTeam.set_top(players['top'][0])
        redTeam.set_jg(players['jng'][0])
        redTeam.set_mid(players['mid'][0])
        redTeam.set_adc(players['adc'][0])
        redTeam.set_sup(players['sup'][0])
        
        blueTeam.set_top(players['top'][1])
        blueTeam.set_jg(players['jng'][1])
        blueTeam.set_mid(players['mid'][1])
        blueTeam.set_adc(players['adc'][1])
        blueTeam.set_sup(players['sup'][1])
        
        self.redTeam = redTeam
        self.blueTeam = blueTeam
        
    # Find fairest team for group of 10 players, swap players in respective roles -> sets new teams
    def findFairestTeams(self):
        
        teamR = self.redTeam
        teamB = self.blueTeam

        best_difference = self.calculateMMRDifference(self.redTeam, self.blueTeam)
        
        for rplayer in teamR.getListPlayers():
            for bplayer in teamB.getListPlayers():
                if rplayer.get_role() == bplayer.get_role():
                    # Swap players
                    role = rplayer.get_role()
                    r_player = rplayer
                    b_player = bplayer
                    if role == 'top':
                        teamR.set_top(b_player)
                        teamB.set_top(r_player)
                    elif role == 'jng':
                        teamR.set_jg(b_player)
                        teamB.set_jg(r_player)
                    elif role == 'mid':
                        teamR.set_mid(b_player)
                        teamB.set_mid(r_player)
                    elif role == 'adc':
                        teamR.set_adc(b_player)
                        teamB.set_adc(r_player)
                    elif role == 'sup':
                        teamR.set_sup(b_player)
                        teamB.set_sup(r_player)
                        
                    # Check MMR difference of new config
                    new_difference = self.calculateMMRDifference(teamR, teamB)
                    
                    # If new config better, swap.
                    if new_difference < best_difference:
                        self.blueTeam = copy.copy(teamR)
                        self.redTeam = copy.copy(teamB)
                        best_difference = new_difference
                
    # MMR Difference Between Both Teams
    def calculateMMRDifference(self, teamR, teamB):
        # Calculate AVG MMR of Init Teams
        teamR.calculateAvgMMR()
        teamB.calculateAvgMMR()
        # Get the AVG MMR of both teams
        btMMR = teamB.get_avgMMR()
        rtMMR = teamR.get_avgMMR()
        # Get the MMR Difference between init teams
        mmrDifference = abs(rtMMR - btMMR)
        return mmrDifference
        
    # Return the details of the current match in string
    def displayMatchDetails(self):
        string = f"   \n✨ MatchID ({self.matchID})\t\t🏅 MMR Difference ({round(self.calculateMMRDifference(self.blueTeam, self.redTeam))})"
        string += f"\n```{'[Blue Team]': ^15}{'':^5}{'[Red Team]':^15}\n\n"
        string += f"{self.blueTeam.get_top().get_username():^15}{'(top)':^5}{self.redTeam.get_top().get_username():^15}\n"
        string += f"{self.blueTeam.get_jg().get_username():^15}{'(jng)':^5}{self.redTeam.get_jg().get_username():^15}\n"
        string += f"{self.blueTeam.get_mid().get_username():^15}{'(mid)':^5}{self.redTeam.get_mid().get_username():^15}\n"
        string += f"{self.blueTeam.get_adc().get_username():^15}{'(adc)':^5}{self.redTeam.get_adc().get_username():^15}\n"
        string += f"{self.blueTeam.get_sup().get_username():^15}{'(sup)':^5}{self.redTeam.get_sup().get_username():^15}\n```"
        
        return string
    
    # Return OPGG Link of Hightest Account per Player()
    def getOPGGLink(self):
        blue_link = self.blueTeam.listOPGG()
        red_link = self.redTeam.listOPGG()
        return blue_link, red_link
    
    async def replacePlayer(self, discordID, otherID, channel, client):
        listOfPlayers = [self.redTeam.getListPlayers() + self.blueTeam.getListPlayers()]
        discordID = int(discordID)
        otherID = int(otherID)
        player_found = False
        # [player(), "red or blue", "jng"]
        team = []
        res = self.cursor.execute(f"SELECT * FROM Player WHERE discordID = {otherID}")
        player_details = res.fetchone()
        try:
            discordUser = await client.fetch_user(player_details[1])
        except:
            discordUser = None
        replacement_player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                   player_details[9], player_details[10], player_details[11], self.cursor, self.con, discordUser)

        
        # Check if player exists in Game
        for player in listOfPlayers:
            for user in player:
               
                if(user.get_dID() == discordID):
                    # If the player does exist, what team?
                    # Red Team
                    for player in self.redTeam.getListPlayers():
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
                    for player in self.blueTeam.getListPlayers():
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
                                
                    new_details = self.displayMatchDetails() 
                    await channel.send(f"{new_details}")
                    player_found = True
                else:
                    pass
            
            
        return player_found
            

        
    
    # Swap two players in a Match
    async def swapPlayers(self, discordID, otherID, message_obj):
        listOfPlayers = [self.redTeam.getListPlayers() + self.blueTeam.getListPlayers()]
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
               
                if(user.get_dID() == discordID or user.get_dID() == otherID):
                    # If the player does exist, what team?
                    # Red Team
                    for player in self.redTeam.getListPlayers():
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
                    for player in self.blueTeam.getListPlayers():
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
            
            #self.findFairestTeams()
            new_details = self.displayMatchDetails() 
            await message_obj.channel.send(f"{new_details}")
            print("done")
        else:
            pass
                
    # Insert initial Match & Set MatchID
    def insert(self):
        res = self.cursor.execute(f"SELECT MAX(matchID) FROM Match")
        latest_matchID = res.fetchone()
        print(latest_matchID)
        if latest_matchID[0] == None:
            matchid = 1
        else:
            matchid = latest_matchID[0] + 1
            
        self.set_matchID(matchid)
        self.startTime = str(datetime.datetime.now().hour) + ":00"
        self.cursor.execute(f"INSERT INTO Match (matchID , matchTime) VALUES ({matchid}, 'TODAY')")
        self.con.commit()
        
    # Delete Match from DB
    def delete(self):
        self.cursor.execute(f"DELETE FROM Match WHERE matchID = {self.matchID}")
        self.con.commit()
        
    # Return list of Players on both team
    def listOfUsers(self):
        listOfPlayers = [self.redTeam.getListPlayers() + self.blueTeam.getListPlayers()]
        listOfUsers = []
        for player in listOfPlayers:
            for user in player:
                listOfUsers.append(user.get_dID())
        return listOfUsers
            
    def resolve(self, winner):
        if winner == 'BLUE':
            winningTeam = self.blueTeam
            losingTeam = self.redTeam
            winner = 1
            self.resolveBets(self.blueBets, self.redBets)
        elif winner == 'RED':
            winningTeam = self.redTeam
            losingTeam = self.blueTeam
            winner = -1
            self.resolveBets(self.redBets, self.blueBets)
        
        MMRdiff = losingTeam.get_avgMMR() - winningTeam.get_avgMMR()
        expectedScore = 1/(1 + 10**(MMRdiff/500))

        kValue = 100
        ratingChange = kValue * (1-expectedScore)
        
        for player in winningTeam.getListPlayers():
            player.fetchPlayerDB()
            player.addWin()
            player.updateRating(ratingChange)
            player.updateLP(ratingChange)
            player.update()

        for player in losingTeam.getListPlayers():
            player.fetchPlayerDB()
            player.addLoss()
            player.updateRating(-ratingChange)
            player.updateLP(-ratingChange)
            player.update()
        self.update(ratingChange, winner)
        
    def update(self, ratingchange, winner):
        playerlist = self.blueTeam.getListPlayers() + self.redTeam.getListPlayers()
        csvnames = ""
        for p in playerlist:
            csvnames += str(p.get_pID()) + ", "
        csvnames += f"'{datetime.datetime.now()}', "
        csvnames += f"{ratingchange*winner}, "*5
        csvnames += f"{ratingchange*-1*winner}, "*4 + f"{ratingchange*-1*winner}"
        self.cursor.execute(f"INSERT INTO Match (bluePOne, bluePTwo, bluePThree, bluePFour, bluePFive, \
    redPOne, redPTwo, redPThree, redPFour, redPFive,\
    matchTime, \
    bluePOneRatingChange, bluePTwoRatingChange, bluePThreeRatingChange, bluePFourRatingChange, bluePFiveRatingChange, \
    redPOneRatingChange, redPTwoRatingChange, redPThreeRatingChange, redPFourRatingChange, redPFiveRatingChange) \
                            VALUES \
                            ({csvnames})")
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
        closingTime = datetime.datetime.now() + datetime.timedelta(minutes=5)
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
                asyncio.create_task(self.respondToBet(user, teamChosen, closingTime))
            except asyncio.TimeoutError:
                bettingClosed = True
        await message.clear_reactions()
        

    async def respondToBet(self, user, team, closingTime):
        if team == "":
            print("this code should be unreachable")
            return
        if team == "BLUE":
            for player in self.redTeam.getListPlayers():
                if player.get_dID() == user.id:
                    await user.send("You can't bet against yourself.")
                    return
        if team == "RED":
            for player in self.blueTeam.getListPlayers():
                if player.get_dID() == user.id:
                    await user.send("You can't bet against yourself.")
                    return
        res = self.con.execute(f"SELECT bettingPoints FROM Player WHERE discordID = {user.id}")
        balance, = res.fetchone()	# I know the comma looks weird here, python syntax for turning a single element tuple into that element is strange

        await user.send(f"How much do you want to bet on team {team} in match {self.matchID} (current balance: {balance}):")
        def check(message):
            return message.author.id == user.id and int(message.content) > 0
        try: 
            msg = await self.client.wait_for('message', check=check, timeout=(closingTime - datetime.datetime.now()).total_seconds())
        except asyncio.TimeoutError:
            await user.send("Out of time.")
            return
        amount = int(msg.content)
        res = self.con.execute(f"SELECT bettingPoints FROM Player WHERE discordID = {user.id}")
        balance, = res.fetchone()	# after any awaits we have to check that the user still has enough to make the bet
        # basically from here to committing the bet is a critical section, no awaits allowed
        if balance < amount:
            await user.send("Insufficient balance")	#except here because we're not committing the bet
            return
        res = self.con.execute(f"UPDATE Player SET bettingPoints = bettingPoints-{amount} WHERE discordID = {user.id}")
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
        await user.send(f"Successfully placed a bet of {amount} on team {team} in match {self.matchID}!")
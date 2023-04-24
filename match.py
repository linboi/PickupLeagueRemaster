from player import Player
from team import Team
import random
import itertools

class Match:
    def __init__(self, matchID, blueTeam, redTeam, startTime, cursor, con):
        
        self.matchID = matchID
        self.blueTeam = blueTeam
        self.redTeam = redTeam
        self.startTime = startTime
        self.cursor = cursor
        self.con = con
        
    def __init__(self, cursor, con):
        
        self.matchID = random.randint(0, 100)
        self.blueTeam = None
        self.redTeam = None
        self.startTime = 'TODAY'
        
        self.cursor = cursor
        self.con = con
        
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
        
    def shuffle_orderPQ(self, playerList, reqPLayers):
        # Shuffle the player list
        random.shuffle(playerList)
        # Use the sorted function to order the list in terms of PQ value
        ordered_pq_list = sorted(playerList, key=lambda p: p.get_QP(), reverse=True)
        # All players left out recieve a +1 PQ Value
        for player in ordered_pq_list[reqPLayers:]:
            print(f"Player Left Out: {player.get_pID()}[{player.get_QP()}]\n")
            player.addQP(1)
            player.update()
        # Return Final List
        return ordered_pq_list[:reqPLayers]
    
    def orderBasedOnMMR(self, selectedPlayerList):
        # Order selected players on MMR
        ordered_rank_list = sorted(selectedPlayerList, key=lambda p: p.get_rating(), reverse=True)
        return ordered_rank_list
        
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
                player.setRoleMMR(0)
            elif len(assigned_roles['jng']) < 2 and player.get_pRole() == 'JNG':
                assigned_roles['jng'].append(player)
                player.set_role('jng')
                player.setRoleMMR(0)
            elif len(assigned_roles['mid']) < 2 and player.get_pRole() == 'MID':
                assigned_roles['mid'].append(player)
                player.set_role('mid')
                player.setRoleMMR(0)
            elif len(assigned_roles['adc']) < 2 and player.get_pRole() == 'ADC':
                assigned_roles['adc'].append(player)
                player.set_role('adc')
                player.setRoleMMR(0)
            elif len(assigned_roles['sup']) < 2 and player.get_pRole() == 'SUP':
                assigned_roles['sup'].append(player)
                player.set_role('sup')
                player.setRoleMMR(0)
            elif len(assigned_roles['top']) < 2 and player.get_sRole() == 'TOP':
                assigned_roles['top'].append(player)
                player.set_role('top')
                player.setRoleMMR(1)
            elif len(assigned_roles['jng']) < 2 and player.get_sRole() == 'JNG':
                assigned_roles['jng'].append(player)
                player.set_role('jng')
                player.setRoleMMR(1)
            elif len(assigned_roles['mid']) < 2 and player.get_sRole() == 'MID':
                assigned_roles['mid'].append(player)
                player.set_role('mid')
                player.setRoleMMR(1)
            elif len(assigned_roles['adc']) < 2 and player.get_sRole() == 'ADC':
                assigned_roles['adc'].append(player)
                player.set_role('adc')
                player.setRoleMMR(1)
            elif len(assigned_roles['sup']) < 2 and player.get_sRole() == 'SUP':
                assigned_roles['sup'].append(player)
                player.set_role('sup')
                player.setRoleMMR(1)
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
                player.setRoleMMR(2)
        
                
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
                        self.blueTeam = teamR
                        self.redTeam = teamB
                        
        print(f"Lowest MMR Difference: {self.calculateMMRDifference(self.blueTeam, self.redTeam)}\n")
        print("\nBlue Team:\n")
        for player in self.blueTeam.getListPlayers():
            print(f"({player.get_role()})[{player.get_pID()}][{player.get_pRole()}][{player.get_sRole()}][{player.get_roleMMR()}]")
        print("\nRed Team:\n")
        for player in self.redTeam.getListPlayers():
            print(f"({player.get_role()})[{player.get_pID()}][{player.get_pRole()}][{player.get_sRole()}][{player.get_roleMMR()}]")
                
        
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
        
    def displayMatchDetails(self):
        string = f"   \n✨ MatchID ({self.matchID})\t \t⏲️ Match Time ({self.startTime})\t \t 🏅 MMR Difference ({round(self.calculateMMRDifference(self.blueTeam, self.redTeam))})"
        string += f"\n```{'[Blue Team]': ^15}{'':^5}{'[Red Team]':^15}\n\n"
        string += f"{self.blueTeam.get_top().get_dID():^15}{'(top)':^5}{self.redTeam.get_top().get_dID():^15}\n"
        string += f"{self.blueTeam.get_jg().get_dID():^15}{'(jng)':^5}{self.redTeam.get_jg().get_dID():^15}\n"
        string += f"{self.blueTeam.get_mid().get_dID():^15}{'(mid)':^5}{self.redTeam.get_mid().get_dID():^15}\n"
        string += f"{self.blueTeam.get_adc().get_dID():^15}{'(adc)':^5}{self.redTeam.get_adc().get_dID():^15}\n"
        string += f"{self.blueTeam.get_sup().get_dID():^15}{'(sup)':^5}{self.redTeam.get_sup().get_dID():^15}\n```"
        opgg_red , opgg_blue = self.getOPGGLink()
        string += f"\n🥶 [Blue Team OPGG]({opgg_blue})\t|\t😡 [Red Team OPGG]({opgg_red})"
        
        return string
    
    def getOPGGLink(self):
        blue_link = self.blueTeam.listOPGG()
        red_link = self.redTeam.listOPGG()
        return blue_link, red_link
    
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
                        redFound = True
                        
                # Blue Team
                for player in self.blueTeam.getListPlayers():
                    if player.get_dID() == discordID:
                        team.append(player)
                        team.append('blue')
                        team.append(player.get_role())
                        blueFound = True
                    elif player.get_dID() == otherID:
                        other_team.append(player)
                        other_team.append('blue')
                        other_team.append(player.get_role())
                        blueFound = True
    
        if blueFound and redFound:
            
            # Parse Players
            #team = team[:len(team)-3]     
            #other_team = other_team[:len(other_team)-3]     
            print(f"{team}")
            print(f"{other_team}")
            # Swap roles
            team[0].set_role(team[2])
            other_team[0].set_role(other_team[2])
            
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
            
            new_details = self.displayMatchDetails() 
            await message_obj.channel.send(f"{new_details}")
                
            
            
        
        
                    
        
        
                        
    
    def insert(self):
        res = self.cursor.execute(f"SELECT MAX(matchID) FROM Match")
        latest_matchID = res.fetchone()
        print(latest_matchID)
        if latest_matchID[0] == None:
            matchid = 1
        else:
            matchid = latest_matchID[0] + 1
            
        self.set_matchID(matchid)
        self.cursor.execute(f"INSERT INTO Match (matchID , matchTime) VALUES ({matchid}, 'TODAY')")
        self.con.commit()
        
    def delete(self):
        self.cursor.execute(f"DELETE FROM Match WHERE matchID = {self.matchID}")
        self.con.commit()
        
    def listOfUsers(self):
        listOfPlayers = [self.redTeam.getListPlayers() + self.blueTeam.getListPlayers()]
        listOfUsers = []
        for player in listOfPlayers:
           for user in player:
            listOfUsers.append(user.get_dID())
        return listOfUsers
            

        
    
        
        
    
    
        
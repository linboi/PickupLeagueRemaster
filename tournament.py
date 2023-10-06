from player import Player
from team import Team
from match import Match
import discord
from wonderwords import RandomWord

class Tournament:
    def __init__(self, cursor, con, client, gameChannel, announcementChannel):
        
        self.cursor = cursor
        self.con = con
        self.client = client
        self.gameChannel = gameChannel
        self.announcementChannel = announcementChannel
        
        # List of tournament teams TTeam()
        self.teams = []
        
        # Bracket Array
        self.bracket = [[TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client)], 
                        [TMatch(self.cursor, self.con, self.client, t_Round=2), TMatch(self.cursor, self.con, self.client, t_Round=2)], 
                        [TMatch(self.cursor, self.con, self.client, t_Round=3)]]
        
        # List of current t_matches
        self.currentTMatches = []
        
        # List of players
        self.playerList = []
        
        # Winner
        self.winner = None
        
    async def generateTeams(self, playerList):
        # Generate a list of balanced teams
        # Add to teams[] TournamentTeam
        # Assign number between 1-8
        # Set current round to 0
        # Generate Random Name (?)
        
        pass
    
    async def testTeam(self):
        # For testing, random id's from db
        discord_id_list = [165186656863780865, 343490464948813824, 413783321844383767, 197053913269010432, 187302526935105536, 574206308803412037, 197058147167371265, 127796716408799232, 180398163620790279,
                           225650967058710529, 618520923204485121, 160471312517562368, 188370105413926912, 694560846814117999, 266644132825530389, 132288462563966977, 355707373500760065, 259820776608235520, 182965319969669120,
                           240994422488170496]
        for idx, id in enumerate(discord_id_list):
            # Create player
            player_details = self.cursor.execute(
                    f"SELECT playerID, discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, QP, isAdmin, missedGames, signupCount, leaderboardPoints, aram_internalRating, aram_leaderboardPoints, aram_winCount, aram_lossCount FROM Player WHERE discordID = {id}").fetchone()

            discordUser = None
            try:
                discordUser = await self.client.fetch_user(player_details[1])
            except:
                discordUser = None
            player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                            player_details[9], player_details[10], player_details[11], player_details[12], player_details[13], player_details[14], player_details[15], self.cursor, self.con, discordUser)
            self.playerList.append(player)
        
        pid = self.playerList.copy()
        for i in range(8):
            team = TTeam(pid[0], pid[1], pid[2], pid[3], pid[4], f"TestName{i}", i)
            self.teams.append(team)
            
        player_details = self.cursor.execute(
                    f"SELECT playerID, discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, QP, isAdmin, missedGames, signupCount, leaderboardPoints, aram_internalRating, aram_leaderboardPoints, aram_winCount, aram_lossCount FROM Player WHERE discordID = {197058147167371265}").fetchone()

        discordUser = None
        try:
            discordUser = await self.client.fetch_user(player_details[1])
        except:
            discordUser = None
        player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                        player_details[9], player_details[10], player_details[11], player_details[12], player_details[13], player_details[14], player_details[15], self.cursor, self.con, discordUser)
        self.playerList.append(player)
        
        self.teams[0].set_top(self.playerList[-1])
        
        player_details = self.cursor.execute(
                    f"SELECT playerID, discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, QP, isAdmin, missedGames, signupCount, leaderboardPoints, aram_internalRating, aram_leaderboardPoints, aram_winCount, aram_lossCount FROM Player WHERE discordID = {225650967058710529}").fetchone()

        discordUser = None
        try:
            discordUser = await self.client.fetch_user(player_details[1])
        except:
            discordUser = None
        player = Player(player_details[0], player_details[1], player_details[2], player_details[3], player_details[4], player_details[5], player_details[6], player_details[7], player_details[8],
                        player_details[9], player_details[10], player_details[11], player_details[12], player_details[13], player_details[14], player_details[15], self.cursor, self.con, discordUser)
        self.playerList.append(player)
        
        self.teams[2].set_top(player)
    
    async def start(self):
        # Create 4 matches based on t_id
        await self.testTeam()
        counter = 0
        for i in range(0, len(self.teams), 2):
            team1 = self.teams[i]
            team2 = self.teams[i+1]
            match = TMatch(self.cursor, self.con, self.client, 202310+i, team1, team2, 'TODAY', 1)
            self.bracket[0][counter] = match
            counter += 1
        
        
        await self.updateBracket()
        await self.displayBracket()
        
        return self.currentTMatches
    
    async def getCurrentMatches(self):
        return self.currentTMatches
    
    async def resolveMatch(self, message, gameID):
        announcement_str = ''
        activePlayerMatches = []
        matchesToAnnounce = []
        activePlayer = message.author.id
        for match in self.currentTMatches:
            for player in match.blueTeam.get_player_list():
                if player.get_dID() == activePlayer:
                    match.setCompleted()
                    match.setWinningSide('BLUE')
                    activePlayerMatches.append((match, 'BLUE'))
            for player in match.redTeam.get_player_list():
                if player.get_dID() == activePlayer:
                    match.setCompleted()
                    match.setWinningSide('RED')
                    activePlayerMatches.append((match, 'RED'))

        if len(activePlayerMatches) == 0:
            await message.channel.send("Player not found in any active tournament matches")
        
        # When player is found, move that team into the next round bracket
        if len(activePlayerMatches) == 1:
            winningTeam = activePlayerMatches[0][0].tResolve(activePlayerMatches[0][1], gameID)
            round = activePlayerMatches[0][0].getRound()
            
            if(winningTeam.getTeamId() <= 4 and round == 1):
                if(self.bracket[1][0].getBlueTeam() is None):
                    self.bracket[1][0].setBlueTeam(winningTeam)
                else:
                    self.bracket[1][0].setRedTeam(winningTeam)
            if(winningTeam.getTeamId() >= 4 and round == 1):
                if(self.bracket[1][1].getBlueTeam() is None):
                    self.bracket[1][1].setBlueTeam(winningTeam)
                else:
                    self.bracket[1][1].setRedTeam(winningTeam)
            if(round == 2):
                if(self.bracket[2][0].getBlueTeam() is None):
                    self.bracket[2][0].setBlueTeam(winningTeam)
                else:
                    self.bracket[2][0].setRedTeam(winningTeam)
            if(round == 3):
                # winner
                self.winner = winningTeam
            
            ratingChange = activePlayerMatches[0][0].resolve(
                activePlayerMatches[0][1], gameID)
            self.currentTMatches.remove(activePlayerMatches[0][0])
            announcement_str += f'🎊 WPGG, remember to upload a post-game screenshot (+{ratingChange:.0f}LP) - You have advanced to the next round!\n'
        
            await self.updateBracket()
            await self.displayBracket(announcement_str)
            
            for match in self.currentTMatches:
                if(match.getAnnouncement() is False and match.getRedTeam() is not None and match.getBlueTeam() is not None):
                    matchesToAnnounce.append(match)
                    
        if len(activePlayerMatches) > 1:
            await message.channel.send("Player found in more than one tournament match, uh oh")
            
        return matchesToAnnounce
        
    async def updateBracket(self):
        # Check each bracket to see if each match has 2 team
        for round in self.bracket:
            for match in round:
                if(match.getCompleted() is False and match.getRedTeam() != None and match.getBlueTeam() != None
                   and match.getAnnouncement() is False):
                    # Side selection based on fastest win?
                    match.setAnnouncement(True)
                    self.currentTMatches.append(match)
                    # Send to game announcement channel
        
        if(self.winner != None):
            # If winner found, announce.
            await self.announcementChannel.send(f"The winner is {self.winner.getTeamName()}")
    
    async def displayBracket(self, anc_str=''):
        bracket_list = []
        for idx, round in enumerate(self.bracket):
            for match in round:
                try:
                    n_bTeam = match.getBlueTeam().getTeamName()
                except:
                    n_bTeam = "T.B.D"
                
                try:
                    n_rTeam = match.getRedTeam().getTeamName()
                except:
                    n_rTeam = "T.B.D"
                
                bracket_list.append(n_bTeam)
                bracket_list.append(n_rTeam)
                
        if(self.winner != None):
            bracket_list.append(self.winner.getTeamName())
            # End tournament
        else:
            bracket_list.append("WINNER")
        
        await self.ascii(bracket_list, anc_str)
                
    async def ascii(self, bracket_list, anc_str):
        new_list = []
        for name in bracket_list:
            new_list.append(await self.reduceName(name))
        
        bracket_list = ''
        bracket_list = new_list.copy()
        
        test = anc_str
        test += f"\n⚔️ PUL Tournament Bracket"
        test += f"```ansi\n"
        test += f"\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[0]}-----':^15}\u001b[0m"
        test +=f"\n{'':^20}\\"
        test +=f"\n{'':^21}\u001b[0;47m\u001b[1;31m-----{bracket_list[8]}-----\u001b[0m"
        test +=f"\n{'':^20}/{'':^20}\\"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[1]}-----':^15}\u001b[0m{'':^22}\\"
        test +=f"\n{'':^43}\u001b[0;40m\u001b[1;36m-----{bracket_list[12]}-----\u001b[0m"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[2]}-----':^15}\u001b[0m{'':^22}/{'':^19}\\"
        test +=f"\n{'':^20}\\{'':^20}/{'':^21}\\"
        test +=f"\n{'':^21}\u001b[0;47m\u001b[1;31m-----{bracket_list[9]}-----\u001b[0m{'':^23}\\"
        test +=f"\n{'':^20}/"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[3]}-----':^15}\u001b[0m"
        test += f"\n{'':^65}(🏆)\u001b[0;40m\u001b[4;32m{bracket_list[14]}\u001b[0m"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[4]}-----':^15}\u001b[0m"
        test +=f"\n{'':^20}\\"
        test +=f"\n{'':^21}\u001b[0;47m\u001b[1;31m-----{bracket_list[10]}-----\u001b[0m{'':^23}/"
        test +=f"\n{'':^20}/{'':^20}\\{'':^21}/"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[5]}-----':^15}\u001b[0m{'':^22}\\{'':^19}/"
        test +=f"\n{'':^43}\u001b[0;40m\u001b[1;36m-----{bracket_list[13]}-----\u001b[0m"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[6]}-----':^15}\u001b[0m{'':^22}/"
        test +=f"\n{'':^20}\\{'':^20}/"
        test +=f"\n{'':^21}\u001b[0;47m\u001b[1;31m-----{bracket_list[11]}-----\u001b[0m"
        test +=f"\n{'':^20}/"
        test += f"\n\u001b[0;41m\u001b[1;37m{f'-----{bracket_list[7]}-----':^20}\u001b[0m```"
        await self.announcementChannel.send(test)
              
    async def displayAllTeams(self):
        # Display op.ggs of teams
        embed_list = []
        for team in self.teams:
            embed_list.append(discord.Embed(
            title =f"{team.getTeamName()} OPGG", url=team.get_multi_opgg(), color=discord.Colour.random()))
        
        for embed in embed_list:
            await self.announcementChannel.send(embed=embed)
            
    async def reduceName(self, input_str):
            # Split the input string by whitespace
        words = input_str.split()

        # Check if there are at least two words
        if len(words) >= 2:
            # Concatenate the first word with the starting character of the next word
            result = words[0] + " " + words[1][0]
        else:
            # If there are not enough words, return the input string as is
            result = input_str

        # Calculate the number of hyphens needed on both sides
        hyphen_count = 10 - len(result)
        if hyphen_count > 0:
            
            left_hyphens = hyphen_count // 2
            right_hyphens = hyphen_count - left_hyphens
            if hyphen_count % 2 == 0:
                result = "-" * left_hyphens + result + "-" * right_hyphens
            else:
                result = "-" * left_hyphens + result + "-" * right_hyphens
        return result
                 
class TTeam(Team):
   def __init__(self, top, jungle, mid, adc, support, t_Name, t_Id):
       super().__init__(top, jungle, mid, adc, support)
       r = RandomWord()
       self.t_name = r.word(word_min_length=2, word_max_length=6, include_parts_of_speech=["adjectives"]).title() + ' ' + r.word(word_min_length=2, word_max_length=6, include_parts_of_speech=["nouns"]).title() + "s"
       self.t_Id = t_Id
       
   def getTeamId(self):
        return self.t_Id
    
   def getTeamName(self):
       if(self.t_name is None):
           return "N/A"
       else:
         return self.t_name
           
class TMatch(Match):
    def __init__(self, cursor, con, client, matchID=None, blueTeam=None, redTeam=None, startTime='TODAY', t_Round=None):
        super().__init__(cursor, con, client, matchID, blueTeam, redTeam, startTime)
        self.round = t_Round
        self.gameLength = None
        self.completed = False
        self.announced = False
        self.winningSide = None
    
    def tResolve(self, winner, gameID):
        if winner == 'BLUE':
            winningTeam = self.blueTeam
        elif winner == 'RED':
            winningTeam = self.redTeam

        return winningTeam
    
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
        round_str=''
        if(self.round == 1):
            round_str = 'QUATER FINALS MATCH'
        if(self.round == 2):
            round_str = 'SEMI FINALS MATCH'
        if(self.round == 3):
            round_str = 'GRAND FINALS MATCH'
        string = f"   \n✨ MatchID ({self.matchID})\t\t🏅 MMR Difference ({round(self.calculateMMRDifference(self.blueTeam, self.redTeam))})\t\t **{round_str}**"
        string += f"\n```{f'[{self.blueTeam.getTeamName()}]': ^15}{'':^5}{f'[{self.redTeam.getTeamName()}]':^15}\n\n"
        string += f"{self.blueTeam.get_top().getMainAccountName():^15}{'(top)':^5}{self.redTeam.get_top().getMainAccountName():^15}\n"
        string += f"{self.blueTeam.get_jg().getMainAccountName():^15}{'(jng)':^5}{self.redTeam.get_jg().getMainAccountName():^15}\n"
        string += f"{self.blueTeam.get_mid().getMainAccountName():^15}{'(mid)':^5}{self.redTeam.get_mid().getMainAccountName():^15}\n"
        string += f"{self.blueTeam.get_adc().getMainAccountName():^15}{'(adc)':^5}{self.redTeam.get_adc().getMainAccountName():^15}\n"
        string += f"{self.blueTeam.get_sup().getMainAccountName():^15}{'(sup)':^5}{self.redTeam.get_sup().getMainAccountName():^15}\n```"
        string += f"{self.tournament_code}"
        for i, invite_string in enumerate(invite_strings):
            string += f"\nInvite list{i}: {invite_string}"

        return string
    
    def setWinningSide(self, side):
        self.winningSide = side
        
    def getWinningSide(self):
        return self.winningSide
    
    def getAnnouncement(self):
        return self.announced
    
    def setAnnouncement(self, ann):
        self.announced = ann
    
    def getRedTeam(self):
        return self.redTeam
    
    def getBlueTeam(self):
        return self.blueTeam
    
    def setRedTeam(self, team):
        self.redTeam = team
    
    def setBlueTeam(self, team):
        self.blueTeam = team
    
    def getRound(self):
        return self.round
    
    def setCompleted(self):
        self.completed = True
        
    def getCompleted(self):
        return self.completed
    
    def setGameLength(self, gameLength):
        self.gameLength = gameLength
    
    def getGameLength(self):
        return self.gameLength    
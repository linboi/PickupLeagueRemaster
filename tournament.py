from player import Player
from team import Team
from match import Match
import discord

class Tournament:
    def __init__(self, cursor, con, client, gameChannel, announcementChannel):
        
        self.cursor = cursor
        self.con = con
        self.client = client
        self.gameChannel = gameChannel
        self.announcementChannel = announcementChannel
        
        
        # List of tournament teams TTeam()
        self.teams = []
        
        self.bracket = [[TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client)], 
                        [TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client)], 
                        [TMatch(self.cursor, self.con, self.client)]]
        
        # List of current t_matches
        self.currentTMatches = []
        
        self.playerList = []
        
        self.discord_id_list = [165186656863780865, 343490464948813824, 413783321844383767, 197053913269010432, 187302526935105536, 574206308803412037, 197058147167371265, 127796716408799232, 180398163620790279,
                           225650967058710529, 618520923204485121, 160471312517562368, 188370105413926912, 694560846814117999, 266644132825530389, 132288462563966977, 355707373500760065, 259820776608235520, 182965319969669120,
                           240994422488170496]
        
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
        for idx, id in enumerate(self.discord_id_list):
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
    
    async def start(self):
        # Create 4 matches based on t_id
        await self.testTeam()
        counter = 0
        for i in range(0, len(self.teams), 2):
            team1 = self.teams[i]
            team2 = self.teams[i+1]
            match = TMatch(self.con, self.cursor, self.client, 202310+i, team1, team2, 'TODAY', 1)
            self.bracket[0][counter] = match
            counter += 1
        
        
        await self.updateBracket()
        await self.displayBracket()
        
        for match in self.currentTMatches:
            match.setAnnouncement(True)
        
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
                if(self.bracket[1][0].getBlueTeam() != None):
                    self.bracket[1][0].setBlueTeam(winningTeam)
                else:
                    self.bracket[1][0].setRedTeam(winningTeam)
            if(winningTeam.getTeamId() >= 4 and round == 1):
                if(self.bracket[1][1].getBlueTeam() != None):
                    self.bracket[1][1].setBlueTeam(winningTeam)
                else:
                    self.bracket[1][1].setRedTeam(winningTeam)
            if(round == 2):
                if(self.bracket[2][0].getBlueTeam() != None):
                    self.bracket[2][0].setBlueTeam(winningTeam)
                else:
                    self.bracket[2][0].setRedTeam(winningTeam)
            if(round == 3):
                # winner
                self.winner = winningTeam
            
            
            self.currentTMatches.remove(activePlayerMatches[0][0])
            announcement_str += f'🎊 WPGG, remember to upload a post-game screenshot - You have advanced to the next round!\n'
            announcement_str += f'__*Updated Leaderbord: Time*__\n'
            
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
        print(len(self.currentTMatches))
        for round in self.bracket:
            for match in round:
                if(match.getCompleted() is False and match.getRedTeam() != None and match.getBlueTeam() != None):
                    # Side selection based on fastest win?
                    
                    self.currentTMatches.append(match)
                    # Send to game announcement channel
        
        if(self.winner != None):
            # If winner found, announce.
            await self.announcementChannel.send(f"The winner is {self.winner.getTeamName()}")
            
    async def displayBracket(self, anc_str=''):
        announcement_str = anc_str
        round_str = ''
        for idx, round in enumerate(self.bracket):
            
            if(idx == 0):
                round_str = f"__Quaters__\n"
            if(idx == 1):
                round_str = f"__Semis__\n"
            if(idx == 2):
                round_str = f"__Finals__\n"
                
            announcement_str += round_str
            for match in round:
                try:
                    n_bTeam = match.getBlueTeam().getTeamName()
                except:
                    n_bTeam = "T.B.D"
                
                try:
                    n_rTeam = match.getRedTeam().getTeamName()
                except:
                    n_rTeam = "T.B.D"
                
                try:
                    if(match.completed is False):
                         announcement_str += f"**{n_bTeam}** *vs.* **{n_rTeam}** : *Finished:{match.getCompleted()}* : *Ann:{match.getAnnouncement()}* \n"
                    else:
                        if(match.getWinningSide() == 'RED'):
                            announcement_str += f"~~**{n_bTeam}**~~ (L) *vs.* **{n_rTeam}** (W) : *Finished:{match.getCompleted()}* : *Ann:{match.getAnnouncement()}* \n"
                        else:
                            announcement_str += f"**{n_bTeam}** (W) *vs.* ~~**{n_rTeam}**~~ (L) : *Finished:{match.getCompleted()}* : *Ann:{match.getAnnouncement()}* \n"
                except:
                    await self.announcementChannel.send(f"Error")
            
        if(self.winner != None):
            announcement_str += f"Winner:{self.winner}"
            #End tournament
        await self.announcementChannel.send(announcement_str)
              
    async def displayAllTeams(self, message):
        # Display op.ggs of teams
        embed_list = []
        
        for team in self.teams:
            embed_list.append(discord.Embed(
            title =f"{team.getTeamName()} OPGG", url=team.get_multi_opgg(), color=discord.Colour.random()))
        
        for embed in embed_list:
            await self.announcementChannel.send(embed=(embed))
           
class TTeam(Team):
   def __init__(self, top, jungle, mid, adc, support, t_Name, t_Id):
       super().__init__(top, jungle, mid, adc, support)
       self.t_name = t_Name
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
            losingTeam = self.redTeam
        elif winner == 'RED':
            winningTeam = self.redTeam
            losingTeam = self.blueTeam

        return winningTeam
    
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
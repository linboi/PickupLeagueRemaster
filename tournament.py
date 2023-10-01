from player import Player
from team import Team
from match import Match
import random


class Tournament:
    def __init__(self, cursor, con, client, gameChannel, announcementChannel):
        
        self.cursor = cursor
        self.con = con
        self.client = client
        self.gameChannel = gameChannel
        self.announcementChannel = announcementChannel
        
        
        # List of tournament teams TTeam()
        self.teams = []
        
        # List of t_matches per round TMatch()
        self.round_1 = [TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client)]
        self.round_2 = [TMatch(self.cursor, self.con, self.client), TMatch(self.cursor, self.con, self.client)]
        self.round_3 = [TMatch(self.cursor, self.con, self.client)]
        
        self.bracket = [self.round_1, self.round_2, self.round_3]
        
        # List of current t_matches
        self.currentTMatches = []
        
        # Winner
        self.winner = None
        
    async def generateTeams(self, playerList):
        # Generate a list of balanced teams
        # Add to teams[] TournamentTeam
        # Assign number between 1-8
        # Set current round to 0
        # Generate Random Name (?)
        pass
    
    async def start(self):
        # Create 4 matches based on t_id
        for i in range(0, len(self.teams), 2):
            team1 = self.teams[i]
            team2 = self.teams[i+1]
            match = TMatch(None, None, None, 202310+i, team1, team2, 'TODAY', 1)
            self.round_1.append(match)
            self.currentTMatches.append(match)
        await self.updateBracket()
        await self.displayBracket()
    
    async def getCurrentMatches(self):
        return self.currentTMatches
    
    async def resolveMatch(self, message, gameID):
        activePlayerMatches = []
        activePlayer = message.author.id
        for match in self.currentTMatches:
            for player in match.blueTeam.get_player_list():
                if player.get_dID() == activePlayer:
                    match.setCompleted()
                    activePlayerMatches.append((match, 'BLUE'))
            for player in match.redTeam.get_player_list():
                if player.get_dID() == activePlayer:
                    match.setCompleted()
                    activePlayerMatches.append((match, 'RED'))

        if len(activePlayerMatches) == 0:
            await message.channel.send("Player not found in any active tournament matches")
        
        # When player is found, move that team into the next round bracket
        if len(activePlayerMatches) == 1:
            winningTeam = activePlayerMatches[0][0].tResolve(activePlayerMatches[0][1], gameID)
            round = activePlayerMatches[0][0].getRound()
            
            if(winningTeam.getTeamId() <= 4 and round == 1):
                if(self.round_2[0].getBlueTeam() != None):
                    self.round_2[0].setBlueTeam(winningTeam)
                else:
                    self.round_2[0].setRedTeam(winningTeam)
            if(winningTeam.getTeamId() >= 4 and round == 1):
                if(self.round_2[1].getBlueTeam() != None):
                    self.round_2[1].setBlueTeam(winningTeam)
                else:
                    self.round_2[1].setRedTeam(winningTeam)
            if(round == 2):
                if(self.round_3[0].getBlueTeam() != None):
                    self.round_3[0].setBlueTeam(winningTeam)
                else:
                    self.round_3[0].setRedTeam(winningTeam)
            if(round == 3):
                # winner
                self.winner = winningTeam
                
            self.currentTMatches.remove(activePlayerMatches[0][0])
            await message.channel.send(f'🎊 WPGG, remember to upload a post-game screenshot - You have advanced to the next round!')
            
        if len(activePlayerMatches) > 1:
            await message.channel.send("Player found in more than one tournament match, uh oh")
            
        await self.updateBracket()
        await self.displayBracket()
    
    async def updateBracket(self):
        # Check each bracket to see if each match has 2 team
        for round in self.bracket:
            for match in round:
                if(match.getCompleted() is False and match.getRedTeam() != None and match.getBlueTeam() != None):
                    # Side selection based on fastest win?
                    self.currentTMatches.append(match)
                    # Send to game announcement channel
        
        if(self.winner != None):
            # If winner found, announce, and end tournament.
            await self.announcementChannel.send(f"The winner is {self.winner.getTeamName()}")
            
    async def displayBracket(self):
        for idx, round in enumerate(self.bracket):
            await self.announcementChannel.send(f"Round({idx})")
            for match in round:
                await self.announcementChannel.send(f"{match.getBlueTeam().getTeamName()} vs. {match.getRedTeam().getTeamName()} ~ {match.getCompleted()}")
        if(self.winner != None):
            await self.announcementChannel.send(f"Winner:{self.winner}")
            
    async def displayAllTeams(self, message):
        # Display op.ggs of teams
        pass
        
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
    
    def tResolve(self, winner, gameID):
        if winner == 'BLUE':
            winningTeam = self.blueTeam
            losingTeam = self.redTeam
        elif winner == 'RED':
            winningTeam = self.redTeam
            losingTeam = self.blueTeam

        return winningTeam
    
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
from player import Player
from team import Team

class Match:
    def __init__(self, matchID, blueTeam, redTeam, startTime):
        
        self.matchID = matchID
        self.blueTeam = blueTeam
        self.redTeam = redTeam
        self.startTime = startTime
        
    def __init__(self):
        
        self.matchID = None
        self.blueTeam = None
        self.redTeam = None
        self.startTime = None
        
    def set_red(self, team):
        self.redTeam = team
        
    def set_blue(self, team):
        self.blueTeam = team
        
    def get_red(self):
        return self.redTeam
    
    def get_blue(self):
        return self.blueTeam
    
    def resolve(self, discordID):
        # Check both teams for player
        
        # Find player -> Find team -> Assign Win/Losses -> Assign MMR Change -> Update Player details -> Set Match Details & Insert into table
        pass
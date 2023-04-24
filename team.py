from player import Player

class Team:
    def __init__(self):
    
        self.top = None
        self.jungle = None
        self.mid = None
        self.adc = None
        self.support = None
        self.avgMMR = 0
        
    # Setters
    def set_avgMMR(self, MMR):
        self.avgMMR = MMR
        
    def set_top(self, player):
        self.top = player
        
    def set_mid(self, player):
        self.mid = player
        
    def set_jg(self, player):
        self.jungle = player
        
    def set_adc(self, player):
        self.adc = player
        
    def set_sup(self, player):
        self.support = player
        
    
    # Getters
    def get_avgMMR(self):
        return self.avgMMR
    
    def get_top(self):
        return self.top
    
    def get_jg(self):
        return self.jungle
    
    def get_mid(self):
        return self.mid
    
    def get_adc(self):
        return self.adc
    
    def get_sup(self):
        return self.support
    
    def calculateAvgMMR(self):
        playerList = self.getListPlayers()
        mmr_sum  = 0
        for player in playerList:
            pMMR = player.get_roleMMR()
            mmr_sum += pMMR
            
        self.set_avgMMR(mmr_sum / 5)
    
    # List of players -> returns array of player objects
    def getListPlayers(self):
        listOfPlayers = [self.top, self.jungle, self.mid, self.adc, self.support]
        return listOfPlayers
        
    # List MULTI OPGG 
    def listOPGG(self):
        players = self.getListPlayers()
        player_string = "https://www.op.gg/multisearch/euw?summoners="
        
        for player in players:
            ign = player.getHighestAccountName()
            player_string += f"{ign}%2C+"
                
        return player_string
                
        
	
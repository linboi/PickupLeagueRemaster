class Team:
    def __init__(self):
    
        self.top = None
        self.jungle = None
        self.mid = None
        self.adc = None
        self.support = None
        
        self.teamMMR = 0
        
    # Setters
    def set_MMR(self, MMR):
        self.MMR = MMR
        
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
    def get_MMR(self):
        return self.teamMMR
    
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
    
    # List of Open Positions
    def fetchOpenPos(self):
        listOfOpenPos = []
        if self.top == None:
            listOfOpenPos.append('TOP')
        if self.jungle == None:
            listOfOpenPos.append('JNG')
        if self.mid == None:
            listOfOpenPos.append('TOP')
        if self.adc == None:
            listOfOpenPos.append('JNG')
        if self.support == None:
            listOfOpenPos.append('TOP')
        return listOfOpenPos
    
    # List of players -> returns array of player objects
    def getListPlayers(self):
        listOfPlayers = [self.top, self.jungle, self.mid, self.adc, self.support]
        return listOfPlayers
        
        
	
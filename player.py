import random

class Player:
    def __init__(self, playerID, discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, playerAccounts, QP, cursor, con):
        self.playerID = playerID
        self.discordID = discordID
        self.winCount = winCount
        self.lossCount = lossCount
        self.internalRating = internalRating
        self.primaryRole = primaryRole
        self.secondaryRole = secondaryRole
        self.playerAccounts = playerAccounts
        self.role = None
        self.roleMMR = None
        self.QP = QP
        
        self.cursor = cursor
        self.con = con
        
        # Sets inital MMR of player
        if self.winCount == 0 and self.lossCount == 0:
            print("Setting InitMMR")
            self.setInitMMR()
            self.update()
            
    # Without player accounts constructor
    def __init__(self, playerID, discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, QP, cursor, con):
        self.playerID = playerID
        self.discordID = discordID
        self.winCount = winCount
        self.lossCount = lossCount
        self.internalRating = internalRating
        self.primaryRole = primaryRole
        self.secondaryRole = secondaryRole
        self.playerAccounts = None
        self.role = None
        self.roleMMR = None
        self.QP = QP
        
        self.cursor = cursor
        self.con = con
        
        # Sets inital MMR of player
        if self.winCount == 0 and self.lossCount == 0:
            print("Setting InitMMR")
            self.setInitMMR()
            self.update()
            
            
    def get_pID(self):
        return self.playerID
    
    def get_dID(self):
        return self.discordID
    
    def get_winCount(self):
        return self.winCount
    
    def get_lossCount(self):
        return self.lossCount
    
    def get_rating(self):
        return self.internalRating
    
    def get_pRole(self):
        return self.primaryRole
    
    def get_sRole(self):
        return self.secondaryRole
    
    def get_pAccounts(self):
        return self.playerAccounts
    
    def get_role(self):
        return self.role
    
    def get_roleMMR(self):
        return self.roleMMR
    
    def reset_QP(self):
        self.QP = 0
        self.update()
    
    def get_QP(self):
        return self.QP
    
    def set_role(self, role):
        self.role = role
        
    def addWin(self):
        self.winCount += 1
        # Calculate MMR Gain -> Set MMR (Enemys AVG MMR)
        
    def addLoss(self):
        self.lossCount += 1
        # Calculate MMR Loss -> Set MMR (Enemys AVG MMR)
        
    def update(self):
        self.cursor.execute(f"UPDATE Player SET winCount = {self.winCount}, lossCount = {self.lossCount}, internalRating = {self.internalRating}, QP = {self.QP} WHERE playerID = {self.playerID}")
        self.con.commit()
        
    def addQP(self, count):
        self.QP += count
        self.update()
        
    def setRoleMMR(self, autofill):
        if autofill == 0:
            self.roleMMR = self.internalRating
        elif autofill == 1:
            self.roleMMR = self.internalRating - 15
        else:
            self.roleMMR = self.internalRating - 30
        
    # Sets the rating of a new player based upon their highest account
    def setInitMMR(self):
        self.QP = 5
        counterNew = 0
        counterOld = 0
        for account in self.playerAccounts:
            
            if account[4] == 'iron':
                counterNew += 0
                counterNew += int(account[5])
                
            if account[4] == 'bronze':
                counterNew += 10
                counterNew += int(account[5])
                
            if account[4] == 'silver':
                counterNew += 20
                counterNew += int(account[5])
                
            if account[4] == 'gold':
                counterNew += 30
                counterNew += int(account[5])
                
            if account[4] == 'platinum':
                counterNew += 40
                counterNew += int(account[5])
                
            if account[4] == 'diamond':
                counterNew += 60
                counterNew += int(account[5])
                
            if account[4] == 'master':
                counterNew += 80
                counterNew += int(account[5])
                
            if account[4] == 'grandmaster':
                counterNew += 100
                counterNew += int(account[5])
                
            if account[4] == 'challenger':
                counterNew += 120
                counterNew += int(account[5])
                
            
            if (counterNew > counterOld):
                counterOld = counterNew
                counterNew = 0
                
        self.internalRating = 1500 + counterOld*5 
        
        

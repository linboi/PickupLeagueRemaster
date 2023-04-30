import random

class Player:

    def __init__(self, playerID, discordID, winCount, lossCount, internalRating, primaryRole, secondaryRole, QP, isAdmin, missedGameCount, signUpCount, LP, cursor, con, discordUser):
        
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
        self.username = None
        self.discordUser = discordUser
        self.LP = LP
        self.isAdmin = isAdmin
        self.signUpCount = signUpCount
        self.missedGameCount = missedGameCount

        
        self.cursor = cursor
        self.con = con
        
        # Set username of Player
        self.set_username()
        
        # Set QP of player
        self.setQP()
        
        
        # Assign Accounts to Player
        self.fetchPlayerAccounts()
        
        # Sets inital MMR of player
        if self.winCount == 0 and self.lossCount == 0:
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
    
    def get_discordUser(self):
        return self.discordID
    
    def get_username(self):
        return self.username
    
    def get_QP(self):
        return self.QP
    
    def get_missedGameCount(self):
        return self.missedGameCount
    
    def get_signUpCount(self):
        return self.signUpCount
    
    def get_LP(self):
        return self.LP
    
    def getAdmin(self):
        return self.isAdmin
    
    def set_username(self):
        try:
            self.username = self.discordUser.name
            print(self.username)
        except:
            self.username = "404"
        
    
    def set_role(self, role):
        self.role = role
        
        # Set RoleMMR based on assigned role
        if role == self.primaryRole.lower():
            self.setRoleMMR(0)
        elif role == self.secondaryRole.lower():
            self.setRoleMMR(1)
        elif self.primaryRole == 'FILL':
            self.setRoleMMR(0)
        elif self.secondaryRole == 'FILL':
            self.setRoleMMR(1)
        else:
            self.setRoleMMR(2)
            
    def addGameMissed(self):
        self.missedGameCount += 1
        self.setQP()
        self.update()
           
    def addSignUpCount(self):
        self.signUpCount += 1
        self.setQP()
        self.update()
           
    def addWin(self):
        self.winCount += 1
        # Calculate MMR Gain -> Set MMR (Enemys AVG MMR)
        
    def addLoss(self):
        self.lossCount += 1
        # Calculate MMR Loss -> Set MMR (Enemys AVG MMR)
        
    def updateLP(self, lp_change):
        self.LP += lp_change
        self.update()
        
    def updateRating(self, rating_change):
        self.internalRating += rating_change
        self.update()
        
    # Updates player in DB
    def update(self):
        self.cursor.execute(f"UPDATE Player SET winCount = {self.winCount}, lossCount = {self.lossCount}, internalRating = {self.internalRating}, QP = {self.QP}, isAdmin = {self.isAdmin}, missedGames = {self.missedGameCount}, signupCount = {self.signUpCount}, leaderboardPoints = {self.LP} WHERE playerID = {self.playerID}")
        self.con.commit()
        
    def setQP(self):
        qp = self.signUpCount - self.missedGameCount
        self.QP = qp
        self.update()
        
    # Sets Role MMR based on Role Preferences
    def setRoleMMR(self, autofill):
        if autofill == 0:
            self.roleMMR = self.internalRating
        elif autofill == 1:
            self.roleMMR = self.internalRating - 200
        else:
            self.roleMMR = self.internalRating - 300
    
    # Get a list of Names from a players Accounts
    def getAccountNames(self):
        listOfNames = []
        for account in self.playerAccounts:
            listOfNames.append(account[1])
        return listOfNames
    
    # Returns the Players highest account name
    def getHighestAccountName(self):
        
        # Tier Mappings
        mappingTiers = {
			'iron': 0,
			'bronze': 400,
			'silver': 800,
			'gold': 1200,
			'platinum': 1600,
			'diamond': 2000,
			'master': 2400,
			'grandmaster': 2400,
			'challenger': 2400
		}
        
        # Div Mappings
        mappingDivs = {
			'1': 300,
			'2': 200,
			'3': 100,
			'4': 0
		}
        
        # Init vars
        acc = None
        counter_old = 0
        counter_new = 0
        
        for account in self.playerAccounts:
            counter_new = 0
            counter_new = mappingTiers[account[4]]
            
            if counter_new >= 2400:
                counter_new += int(account[5])
            else:
                counter_new += mappingDivs[account[5]]
                
            if counter_new > counter_old:
                counter_old = counter_new
                acc = account[1]
        
        return acc
    
    def fetchPlayerAccounts(self):
        res = self.cursor.execute(f"SELECT * FROM Account WHERE playerID = {self.playerID}")
        result = res.fetchall()
        self.playerAccounts = result
        
    # Sets the rating of a new player based upon their highest account
    def setInitMMR(self):
        
        # Tier Mappings
        mappingTiers = {
			'iron': 0,
			'bronze': 400,
			'silver': 800,
			'gold': 1200,
			'platinum': 1600,
			'diamond': 2000,
			'master': 2400,
			'grandmaster': 2800,
			'challenger': 3200
		}
        
        # Div Mappings
        mappingDivs = {
			'1': 300,
			'2': 200,
			'3': 100,
			'4': 0
		}
        
        # Init counters
        counter_old = 0
        counter_new = 0
        
        for account in self.playerAccounts:
            counter_new = 0
            counter_new = mappingTiers[account[4]]
            
            if counter_new >= 2400:
                counter_new += int(account[5])
            else:
                counter_new += mappingDivs[account[5]]
            
            if counter_new > counter_old:
                counter_old = counter_new
        
        self.internalRating = counter_new
        
        
        

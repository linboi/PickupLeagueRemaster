from player import Player


class Team:

    def __init__(self):

        self.top = None
        self.jungle = None
        self.mid = None
        self.adc = None
        self.support = None
        self.avgMMR = 0

    def __init__(self, top, jungle, mid, adc, support):

        top.set_role("TOP")
        self.top = top
        jungle.set_role("JNG")
        self.jungle = jungle
        mid.set_role("MID")
        self.mid = mid
        adc.set_role("ADC")
        self.adc = adc
        support.set_role("SUP")
        self.support = support
        # for player in self.getListPlayers():
        # player.set_role
        # self.calculateAvgMMR()

    # Setters
    def set_avgMMR(self, MMR):
        self.avgMMR = MMR

    def set_top(self, player):
        self.top = player
        self.top.set_role("top")

    def set_mid(self, player):
        self.mid = player
        self.mid.set_role("mid")

    def set_jg(self, player):
        self.jungle = player
        self.jungle.set_role("jng")

    def set_adc(self, player):
        self.adc = player
        self.adc.set_role("adc")

    def set_sup(self, player):
        self.support = player
        self.support.set_role("sup")

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

    # Sets AVGMMR of the Team
    def calculateAvgMMR(self):
        playerList = self.getListPlayers()
        mmr_sum = 0
        for player in playerList:
            pMMR = player.get_roleMMR()
            mmr_sum += pMMR

        self.set_avgMMR(mmr_sum / 5)

    # List of players -> returns array of player objects
    def getListPlayers(self):
        listOfPlayers = [self.top, self.jungle,
                         self.mid, self.adc, self.support]
        return listOfPlayers

    # List MULTI OPGG
    def listOPGG(self):
        players = self.getListPlayers()
        player_string = "https://www.op.gg/multisearch/euw?summoners="
        ign = ""
        for player in players:
            ign = player.getHighestAccountName()
            if ign == None:
                ign = "placeholder"
            ign = ign.replace(" ", "+")
            player_string += f"{ign}%2C+"

        return player_string

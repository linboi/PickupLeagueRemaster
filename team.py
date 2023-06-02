class Team:
    def __init__(self, top, jungle, mid, adc, support):
        self.set_top(top)
        self.set_jg(jungle)
        self.set_mid(mid)
        self.set_adc(adc)
        self.set_sup(support)

    # Setters
    def set_avg_MMR(self, MMR):
        self.avg_MMR = MMR

    def set_top(self, player):
        self.top = player
        self.top.set_role("top")

    def set_jg(self, player):
        self.jungle = player
        self.jungle.set_role("jng")

    def set_mid(self, player):
        self.mid = player
        self.mid.set_role("mid")

    def set_adc(self, player):
        self.adc = player
        self.adc.set_role("adc")

    def set_sup(self, player):
        self.support = player
        self.support.set_role("sup")

    # Getters
    def get_avg_MMR(self):
        self.calculate_avg_MMR()
        return self.avg_MMR

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

    def calculate_avg_MMR(self):
        total_MMR = 0
        player_list = self.get_player_list()
        for player in player_list:
            total_MMR += player.get_roleMMR()
        self.set_avg_MMR(total_MMR / 5)

    def get_player_list(self):
        players = [self.top, self.jungle,
                   self.mid, self.adc, self.support]
        return players

    def get_multi_opgg(self):
        players = self.get_player_list()
        multi_opgg = "https://www.op.gg/multisearch/euw?summoners="
        for player in players:
            username = player.getHighestAccountName()
            if username != None:
                username = username.replace(" ", "+")
                multi_opgg += f"{username},"
            else:
                print(f"No opgg found for  {player}")
        return multi_opgg

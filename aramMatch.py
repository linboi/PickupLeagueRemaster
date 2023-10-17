import datetime
import random


class ARAM_Team:
    def __init__(self, players):
        self.players = players

    def get_avg_MMR(self):
        total = 0
        for player in self.players:
            total += player.ARAM_rating
        return total/5

    def get_player_list(self):
        return self.players


class ARAM_Match:
    champsPerTeam = 10

    def __init__(self, cursor, con, client, matchID=None, blueTeam=None, redTeam=None, startTime='TODAY'):

        self.matchID = matchID
        self.blueTeam = blueTeam
        self.redTeam = redTeam
        self.startTime = startTime
        self.cursor = cursor
        self.con = con
        self.blueBets = {}
        self.redBets = {}
        self.client = client
        self.tournament_code = None
        with open("./champList.txt", "r") as f:
            champList = f.read().splitlines()
            random.shuffle(champList)
            self.blueChamps = champList[0:ARAM_Match.champsPerTeam]
            self.redChamps = champList[ARAM_Match.champsPerTeam:2 *
                                       ARAM_Match.champsPerTeam]

    def __repr__(self):
        return self.get_details_string()

    def get_details_string(self):
        discordIDs = ", ".join(str(x) for x in self.listOfUsers())
        res = self.cursor.execute(
            f"SELECT [name] FROM Account JOIN Player ON Account.playerID = Player.playerID WHERE Player.discordID in ({discordIDs})").fetchall()
        invite_strings = []
        idx = 0
        while idx < len(res):
            invite_string = ",".join(
                str(name[0]) for name in res[idx:min(len(res)-1, idx+10)])
            invite_strings.append(invite_string)
            idx += 10
        string = f"   \n✨ MatchID ({self.matchID})\t\t🏅 MMR Difference ({round(self.calculateMMRDifference(self.blueTeam, self.redTeam))})"
        string += f"\n```{'[Blue Team]': ^15}{'':^5}{'[Red Team]':^15}\n\n"
        for i, p in enumerate(self.blueTeam.players):
            string += f"{self.blueTeam.players[i].get_username():^15}\t{self.redTeam.players[i].get_username():^15}\n"
        string += f"```"
        string += f"```{'[Blue Champs]': ^15}{'':^5}{'[Red Champs]':^15}\n"
        for i, c in enumerate(self.blueChamps):
            string += f"{self.blueChamps[i].upper():^15}\t{self.redChamps[i].upper():^15}\n"
        string += f"```"
        for i, invite_string in enumerate(invite_strings):
            string += f"\nInvite list{i}: {invite_string}"

        return string

    def listOfUsers(self):
        listOfPlayers = [self.redTeam.players +
                         self.blueTeam.players]
        listOfUsers = []
        for player in listOfPlayers:
            for user in player:
                listOfUsers.append(user.get_dID())
        return listOfUsers

    def resolve(self, winner, gameID):
        if winner == 'BLUE':
            winningTeam = self.blueTeam
            losingTeam = self.redTeam
            # self.resolveBets(self.blueBets, self.redBets)
        elif winner == 'RED':
            winningTeam = self.redTeam
            losingTeam = self.blueTeam
            # self.resolveBets(self.redBets, self.blueBets)

        MMRdiff = losingTeam.get_avg_MMR() - winningTeam.get_avg_MMR()
        expectedScore = 1/(1 + 10**(MMRdiff/500))

        kValue = 100
        ratingChange = kValue * (1-expectedScore)

        for player in winningTeam.get_player_list():
            disc = player.get_dID()
            self.cursor.execute(
                f"UPDATE Player SET aram_winCount = aram_winCount + 1, aram_internalRating = aram_internalRating + {ratingChange}, aram_leaderboardPoints = aram_leaderboardPoints + {ratingChange} WHERE discordID = {disc}")
            self.con.commit()

        for player in losingTeam.get_player_list():
            disc = player.get_dID()
            self.cursor.execute(
                f"UPDATE Player SET aram_lossCount = aram_lossCount + 1, aram_internalRating = aram_internalRating - {ratingChange}, aram_leaderboardPoints = aram_leaderboardPoints - {ratingChange} WHERE discordID = {disc}")
            self.con.commit()

        self.update(ratingChange, winningTeam, losingTeam, winner, gameID)
        return ratingChange

    def update(self, ratingchange, winningTeam, losingTeam, winner, gameID):
        if winner != 'BLUE':
            loser = 'BLUE'
        else:
            loser = 'RED'
        self.cursor.execute(
            f"UPDATE Match SET resolutionTime = '{datetime.datetime.now()}', gameID = {gameID} WHERE matchID = {self.matchID}")
        for p in winningTeam.get_player_list():
            self.cursor.execute(f"""INSERT INTO PlayerMatch (playerID, matchID, ratingChange, [role], team)
                                    VALUES ({p.get_pID()}, {self.matchID}, {ratingchange}, 'ARAM', '{winner}')""")
        for p in losingTeam.get_player_list():
            self.cursor.execute(f"""INSERT INTO PlayerMatch (playerID, matchID, ratingChange, [role], team)
                                    VALUES ({p.get_pID()}, {self.matchID}, {-ratingchange}, 'ARAM', '{loser}')""")
        self.con.commit()

    # Use this code when we swap to using the DB instead of objects
    # def calculateMMRDifference(self, blue, red):
    #    discIDs = ",".join(str(x) for x in self.blueTeam)
    #    blueMMR = self.cursor.execute(f"SELECT sum(aram_internalRating) FROM Player WHERE discordID in ({discIDs})").fetchall()
    #    discIDs = ",".join(str(x) for x in self.redTeam)
    #    redMMR = self.cursor.execute(f"SELECT sum(aram_internalRating) FROM Player WHERE discordID in ({discIDs})").fetchall()
    #    return (blueMMR + redMMR)/5

    # MMR Difference Between Both Teams
    def calculateMMRDifference(self, teamR, teamB):
        # Get the AVG MMR of both teams
        btMMR = teamB.get_avg_MMR()
        rtMMR = teamR.get_avg_MMR()
        # Get the MMR Difference between init teams
        mmrDifference = abs(rtMMR - btMMR)
        return mmrDifference

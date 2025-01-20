from player import Player
from table2ascii import PresetStyle
from table2ascii import table2ascii as t2a


class Stats:
    def __init__(self):
        pass

    # Base command just wants number of games, winrate, banrate, KDA
    async def getChampionStats(self, message, season):
        res = self.cursor.execute(f"""
                                SELECT champion, SUM(kills), SUM(deaths), SUM(assists), count(champion) as Games, 
                                SUM(CASE WHEN TEST > 0 THEN 1
                                ELSE 0
                                END) AS winCount,
                                SUM(CASE WHEN TEST < 0 THEN 1
                                ELSE 0
                                END) AS lossCount
                                WHERE (season = {season} OR {season} = 0)
                                GROUP BY champion
                                ORDER BY Games DESC, winRate DESC
                                """).fetchall()
        output = t2a(header=["Champion", "Kills", "Deaths", "Assists", "KDA", "Games", "Win Rate", "Ban Rate", "W/L", ],
                     body=[[] for x in res],
                     style=PresetStyle.thin_compact,
                     first_col_heading=True)
        await message.channel.send(f"```\n{output}\n```")

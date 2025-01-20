import requests
import time
from bs4 import BeautifulSoup
import random
import sys
import re


def getMMRFromRank(rankTier, rankDiv, rankLP):
    mappingTiers = {
        'iron': 0,
        'bronze': 400,
        'silver': 800,
        'gold': 1200,
        'platinum': 1600,
        'emerald': 2000,
        'diamond': 2400,
        'master': 2500,
        'grandmaster': 2500,
        'challenger': 2500
    }

    # Div Mappings
    mappingDivs = {
        '1': 300,
        '2': 200,
        '3': 100,
        '4': 0
    }
    return mappingTiers[rankTier] + mappingDivs[rankDiv] + rankLP


def scrapeRanksFromLOG(gamename, tagline):
    rankList = []
    # Assign Headers, so scraping is not BLOCKED
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    try:
        log_url = f"https://www.leagueofgraphs.com/summoner/euw/{gamename}-{tagline}"
        res_url = requests.get(log_url, headers=headers)
        doc = BeautifulSoup(res_url.text, "html.parser")
        time.sleep(random.uniform(2, 4))
    except:
        pass
    div_tags = doc.find_all('div', class_='tag requireTooltip brown')
    for box in div_tags:
        tooltip = box.get('tooltip')
        tooltip_soup = BeautifulSoup(tooltip, 'html.parser')

        description = tooltip_soup.select_one('.tagDescription')
        for match in re.compile(r'(.+?)This player reached (.+?) during (.+?)\. At the end of the season, this player was (.+?)\.').finditer(description.get_text()):
            queue, peak, season, endOfSeasonRank = match.groups()
            tier, div, Lp = parseRank(peak)
            rankList.append((queue, tier, div, Lp, season))

    return rankList


def roman_to_int(roman):
    roman_nums = {
        'I': 1,
        'II': 2,
        'III': 3,
        'IV': 4
    }
    return roman_nums[roman]


def parseRank(text):
    Lp = 0
    try:
        tier, div = text.split(' ')
        if div.endswith('LP'):
            Lp = int(div[0:-2:])
            div = 'I'
    except ValueError:
        return text, 1, 0
    return tier, roman_to_int(div), Lp


def getCurrentRank(gamename, tagline, apiKey):
    puuid = None
    rankList = []
    # First, get the encrypted summoner ID
    summoner_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gamename}/{tagline}?api_key={apiKey}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com"
    }

    try:
        resp = requests.get(summoner_url, headers)

        resp.raise_for_status()

        puuid = resp.json().get('puuid')

        account_url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={apiKey}"

        acc_id_resp = requests.get(account_url, headers)

        acc_id_resp.raise_for_status()

        acc_id = acc_id_resp.json().get('id')

        ranked_info_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{acc_id}?api_key={apiKey}"

        ranked_info = requests.get(ranked_info_url, headers)

        ranked_info.raise_for_status()

        # Find the solo queue entry
        for queue in ranked_info.json():
            if queue['queueType'] == 'RANKED_SOLO_5x5':
                rankList.append(('Ranked Solo/Duo', queue['tier'], roman_to_int(
                    queue['rank']), queue['leaguePoints'], 'Current Season'))
            if queue['queueType'] == 'RANKED_FLEX_SR':
                rankList.append(('Ranked Flex', queue['tier'], roman_to_int(
                    queue['rank']), queue['leaguePoints'], 'Current Season'))
        return rankList
    except Exception as e:
        # Better error handling: print the actual error
        print(f"API Request Failed: {str(e)}")


def getAllRanks(gamename, tagline, apiKey):
    return scrapeRanksFromLOG(gamename, tagline) + getCurrentRank(gamename, tagline, apiKey)


def main():
    res = getAllRanks(sys.argv[1], sys.argv[2],
                      "RGAPI-6877edc1-cb3e-4c0f-8e09-2aa8d1860969")
    for line in res:
        print(line)


if __name__ == '__main__':
    main()

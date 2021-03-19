from bs4 import BeautifulSoup
import requests
import re
import sys

#---------------------------------------------------------------------#
# This script takes names of faceit profiles and averages the usefull stats
# for all names mentioned over active maps
#---------------------------------------------------------------------#
# Website Dependencies: faceitelo.net
# If pyhton isn't installed go to https://www.python.org/downloads/ and press big yellow download button
# Remember to check the box with "add python 3.9 to PATH when installing"
# Module dependencies:(run commands below if module missing)
#   pip install bs4
#   pip install requests
#---------------------------------------------------------------------#
# To Run scipt:
# Open CMD
# Make shure you have the script in the folder you are currentley in (shown in console)
# Type following in CMD: py Faceit_pug_scraper name name name
# "name" should be replaced with all players you want to include in the script

# FLAGS(add after names if wanted):
#    -p sorts maps by lowest avg times map played
#    -w sorts maps by lowest avg winrate
#    -p sorts maps by lowest avg kills
#---------------------------------------------------------------------#
ACTIVE_MAP_POOL = ["de_inferno", "de_mirage", "de_train",
                   "de_overpass", "de_nuke", "de_vertigo", "de_dust2"]


def extractplayerstats(name):

    playername = name
    page = requests.get("https://faceitelo.net/player/" + playername)
    soup = BeautifulSoup(page.content, 'html.parser')
    textwall = soup.get_text()
    map_plays_winrate_avgkills = {}

    for map in ACTIVE_MAP_POOL:
        map_plays_winrate_avgkills[map] = []
        #janky ass tag system of website makes bs4 navigation useless
        #regex used instead
        match = re.search(" "
                          + map
                          + "\n(.*?)\n([0-9]{2})%\n.*?\n.*?\nK:([0-9.]+)",
                          textwall)
        map_plays_winrate_avgkills[map].append(match.group(1))
        map_plays_winrate_avgkills[map].append(match.group(2))
        map_plays_winrate_avgkills[map].append(match.group(3))

    return map_plays_winrate_avgkills


def pretty_mapdata_print(mapdata):
    # MAP
    #   Stat : val
    #   ...
    # ...
    for map in mapdata:
        print(map.upper())
        for stat in mapdata[map]:
            print("     " + stat + " : " + str(mapdata[map][stat]))


def main():
    players = {}
    mapdata = {}
    indata = sys.argv
    flags = []
    # catch flags from indata and remove
    for data in indata:
        if data[0] == "-":
            flags.append(data)
            indata.remove(data)
    # Get stats for all palyers
    for name in sys.argv[1:]:
        players[name] = extractplayerstats(name)
    # Average out all stats over active maps
    for map in ACTIVE_MAP_POOL:
        stat_avg = {"avg_plays": [], "avg_winrate": [], "avg_kills": []}
        stat_keys = list(stat_avg.keys())
        for player in players:
            for i in range(len(stat_avg)):
                stat_avg[stat_keys[i]].append(float(players[player][map][i]))
        for avg in stat_avg:
            stat_avg[avg] = sum(stat_avg[avg])/len(stat_avg[avg])

        mapdata[map] = stat_avg
    #sortbyflag
    for flag in flags:
        sort_by = {"-p": "avg_plays",
                   "-w": "avg_winrate",
                   "-k": "avg_kills"}.get(flag, None)
        if sort_by is not None:
            mapdata = {map: data for map, data in sorted(mapdata.items(), key=lambda item: item[1][sort_by])}
    pretty_mapdata_print(mapdata)

if __name__ == '__main__':
    main()

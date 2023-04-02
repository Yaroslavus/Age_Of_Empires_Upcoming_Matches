from urllib.request import urlopen
from html.parser import HTMLParser
from dataclasses import dataclass
from calendar import month_abbr
import re


AOE_liquipedia_prefix = "https://liquipedia.net"
AOE_liquipedia_URL = AOE_liquipedia_prefix + "/ageofempires/Age_of_Empires_II"


@dataclass
class Tournament:
    tier: str = None
    title: str = None
    date: str = None
    link: str = None
    prize: str = None
    participants_number: str = None
    location: str = None
    live: bool = False
    winner: str = None
    runner_up: str = None


@dataclass
class Game:
    team_1: str = None
    team_2: str = None
    time: str = None
    stage: str = None


class MainPageParser(HTMLParser):

    def __init__(self, site_name, *args, **kwargs):
        self.tagStack = []
        self.TOURNAMENTS = []
        self.tiers = self.titles = self.dates = self.links = self.prizes = []
        self.participants = self.locations = self.winners = self.runner_ups = []
        self.location_flag = self.participants_flag = self.runner_up_flag = False
        self.date_flag = self.prize_flag = self.winner_flag = False
        self.site_name = site_name
        super().__init__(*args, **kwargs)
        self.feed(self.read_site_content())

    def read_site_content(self):
        return str(urlopen(self.site_name).read())

    def handle_tourhament_data(self, tag, attrs):
        if (tag == 'a') and (self.tagStack[-2] == 'b'):
            link = AOE_liquipedia_prefix + attrs[0][1]
            self.links.append(link)
            self.TOURNAMENTS[-1].link = link

        elif (tag == 'a') and attrs and len(attrs) == 2 and (attrs[0][0] == 'href') and (attrs[1][0] == 'title'):
            tier = attrs[1][1].split('/')[-1]
            if (tier == 'S-Tier Tournaments') or (tier == 'A-Tier Tournaments'):
                self.tiers.append(tier.split()[0])
                self.TOURNAMENTS[-1].tier = tier.split()[0]

        elif (tag == 'a') and attrs and len(attrs) == 2 and (attrs[0][0] == 'href') and (attrs[1][0] == 'title'):
            location = attrs[0][1].split("Category:")
            if len(location) == 2:
                self.locations.append(location[1])
                self.TOURNAMENTS[-1].location = location[1]

    def is_live(self, data):
        return True

    def handle_data(self, data):
        if (self.tagStack[-2:] == ['b', 'a']):
            self.titles.append(data)
            self.TOURNAMENTS[-1].title = data

        if self.date_flag:
            self.dates.append(data)
            self.TOURNAMENTS[-1].date = data
            self.date_flag = False
            if self.is_live(data):
                self.TOURNAMENTS[-1].live = True

        if self.prize_flag:
            self.prizes.append(data)
            self.TOURNAMENTS[-1].prize = data
            self.prize_flag = False

        if self.participants_flag:
            self.participants.append(data)
            self.TOURNAMENTS[-1].participants_number = data
            self.participants_flag = False

        if self.location_flag:
            self.locations.append(data)
            self.TOURNAMENTS[-1].location = data
            self.location_flag = False

        if self.winner_flag:
            self.winners.append(data)
            self.TOURNAMENTS[-1].winner = data
            self.winner_flag = False

        if self.runner_up_flag:
            self.runner_ups.append(data)
            self.TOURNAMENTS[-1].runner_up = data
            self.runner_up_flag = False

    def handle_starttag(self, tag, attrs):
        if (not self.tagStack) and (tag == 'div') and (attrs == [("class", "divRow")]):
            self.tagStack = []
            self.tagStack.append(tag)
            tournament = Tournament()
            self.TOURNAMENTS.append(tournament)
        elif (self.tagStack) and (self.tagStack[0] == 'div'):
            self.tagStack.append(tag)
            if (attrs == [("class", "divCell EventDetails Date Header")]):
                self.date_flag = True
            elif (attrs == [("class", "divCell EventDetails Prize Header")]):
                self.prize_flag = True
            elif (attrs == [("class", "divCell EventDetails PlayerNumber Header")]):
                self.participants_flag = True
            elif (attrs == [("class", "divCell EventDetails Location Header")]):
                self.location_flag = True
            elif (attrs == [("class", "divCell Placement FirstPlace")]):
                self.winner_flag = True
            elif (attrs == [("class", "divCell Placement SecondPlace")]):
                self.runner_up_flag = True
            self.handle_tourhament_data(tag, attrs)
#        if self.tagStack: print(self.tagStack)           # PRINT MAIN tagStack

    def handle_endtag(self, endTag):
        if (self.tagStack) and (endTag == self.tagStack[-1]):
            self.tagStack.pop()


class TournamentPageParser(HTMLParser):
    def __init__(self, site_name, *args, **kwargs):
        self.tagStack = []
        self.GAMES = []
        self.team_1 = self.team_2 = self.stages = self.times = []
        self.team_1_flag = self.team_2_flag = self.time_flag = self.stage_flag = False
        self.site_name = site_name
        super().__init__(*args, **kwargs)
        self.feed(self.read_site_content())

    def read_site_content(self):
        return str(urlopen(self.site_name).read())

    def handle_game_data(self, tag, attrs):
        if (tag == 'span') and attrs and len(attrs) == 2:
            team_1 = attrs[0][1]
            print("HERE team 1")
            print("TEAM1: ", team_1)
            self.team_1.append(team_1)
            self.GAMES[-1].team_1 = team_1
            self.team_1_flag = False

        if (tag == 'span') and attrs and len(attrs) == 2 and (attrs[0][0] == 'data-highlightingclass') and (attrs[1][0] == 'class') and self.team_2_flag:
            team_2 = attrs[0][1]
            print("HERE team 2")
            print("TEAM2: ", team_2)
            self.team_2.append(team_2)
            self.GAMES[-1].team_2 = team_2
            self.team_2_flag = False

    def handle_data(self, data):
        if self.time_flag:
            print("HERE time")
            print("TIME: ", data)
            self.times.append(data)
            self.GAMES[-1].time = data

    def handle_starttag(self, tag, attrs):
        if (not self.tagStack) and (tag == 'table') and (attrs == [("class", "wikitable wikitable-striped infobox_matches_content")]):
            self.tagStack = []
            self.tagStack.append(tag)
            game = Game()
            self.GAMES.append(game)
        elif (self.tagStack) and (self.tagStack[0] == 'table'):
            self.tagStack.append(tag)

            if (attrs == [("class", "team-left")]):
                self.team_1_flag = True
            elif (attrs == [("class", "team-right")]):
                self.team_2_flag = True
            elif (attrs == [("class", "timer-object timer-object-countdown-only")]):
                self.time_flag = True
            self.handle_game_data(tag, attrs)
#        if self.tagStack: print(self.tagStack)           # PRINT MAIN tagStack

    def handle_endtag(self, endTag):
        if (self.tagStack) and (endTag == self.tagStack[-1]):
            self.tagStack.pop()



def main():
    tournaments = MainPageParser(AOE_liquipedia_URL)
    for tour in tournaments.TOURNAMENTS:
        print(tour.title)
        games = TournamentPageParser(tour.link)
        for game in games.GAMES:
            print(game, '\n\n')

if __name__ == "__main__":
    main()
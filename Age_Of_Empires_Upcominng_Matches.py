from urllib.request import urlopen
from html.parser import HTMLParser
from dataclasses import dataclass
import calendar
import re
import datetime


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
    live: str = None
    winner: str = None
    runner_up: str = None


@dataclass
class Game:
    team_1: str = None
    team_2: str = None
    time: str = None
    stage: str = None
    live: str = None


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
        def to_local_datetime(utc_dt):
            return datetime.datetime.fromtimestamp(calendar.timegm(utc_dt.timetuple()))
        days = re.findall(re.compile(r'[\s,-](\d{2})[\s,-]'), data)
        days = days if len(days) == 2 else days*2
        years = re.findall(re.compile(r'(\d{4})'), data)
        years = years*2 if len(years) == 1 else years
        monthes = [list(calendar.month_abbr).index(word) for word in data.split() if word in list(calendar.month_abbr)[1:]]
        monthes = monthes*2 if len(monthes) == 1 else monthes

        start_datetime = datetime.datetime.strptime(f'{days[0]}.{monthes[0]}.{years[0][2:]}', '%d.%m.%y')
        finish_datetime = datetime.datetime.strptime(f'{days[1]}.{monthes[1]}.{years[1][2:]}', '%d.%m.%y')
        start_datetime_local = to_local_datetime(start_datetime)
        finish_datetime_local = to_local_datetime(finish_datetime)
        now = datetime.datetime.now()
        if (now > start_datetime_local) and (now < finish_datetime_local):
            return "LIVE!"
        elif (now < start_datetime_local) and (now < finish_datetime_local):
            return "Soon..."
        elif (now > start_datetime_local) and (now > finish_datetime_local):
            return "Finished"

    def handle_data(self, data):
        if (self.tagStack[-2:] == ['b', 'a']):
            self.titles.append(data)
            self.TOURNAMENTS[-1].title = data

        if self.date_flag:
            self.dates.append(data)
            self.TOURNAMENTS[-1].date = data
            self.TOURNAMENTS[-1].live = self.is_live(data)
            self.date_flag = False

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

    def handle_endtag(self, endTag):
        if (self.tagStack) and (endTag == self.tagStack[-1]):
            self.tagStack.pop()


class TournamentPageParser(HTMLParser):
    def __init__(self, site_name, *args, **kwargs):
        self.tagStack = []
        self.GAMES = []
        self.team_1 = self.team_2 = self.stage = self.time = []
        self.team_1_flag = self.team_2_flag = self.time_flag = False
        self.stage_flag = self.flag_flag = False
        self.site_name = site_name
        super().__init__(*args, **kwargs)
        self.feed(self.read_site_content())

    def read_site_content(self):
        return str(urlopen(self.site_name).read())

    def is_live(self, data):
        days = re.findall(re.compile(r'[\s,-](\d{2})[\s,-]'), data)
        years = re.findall(re.compile(r'(\d{4})'), data)
        monthes = [list(calendar.month_abbr).index(word[:3]) for word in data.split() if word in list(calendar.month_abbr)[1:]]
        time = re.findall(re.compile(r'(\d{2}:\d{2})'), data)
        print(days, monthes, years, time)
        start_datetime = datetime.datetime.strptime(f'{days[0]}.{monthes[0]}.{years[0][2:]}', '%d.%m.%y')
        start_timestamp = datetime.datetime.timestamp(start_datetime)
        finish_timestamp = start_timestamp
        now = datetime.datetime.timestamp(datetime.datetime.now())
        if (now > start_timestamp) and (now < finish_timestamp):
            return "LIVE!"
        elif (now < finish_timestamp) and (now < finish_timestamp):
            return "Soon..."
        elif (now > finish_timestamp) and (now > finish_timestamp):
            return "Finished"

    def handle_game_data(self, tag, attrs):
        if self.team_1_flag and (tag == 'a') and attrs and (attrs[0][0] == 'href') and (attrs[-1][0] == 'title'):
            if not (self.flag_flag):
                team_1 = attrs[-1][1] if ('(page does not exist)' not in attrs[-1][1]) else attrs[-1][1][:-22]
#               print("HERE team 1")
#               print("TEAM1: ", team_1)
                self.team_1.append(team_1)
                self.GAMES[-1].team_1 = team_1
                self.team_1_flag = False
            else:
                self.flag_flag = False

        if self.team_2_flag and (tag == 'a') and attrs and (attrs[0][0] == 'href') and (attrs[-1][0] == 'title'):
            if not (self.flag_flag):
                team_2 = attrs[-1][1] if ('(page does not exist)' not in attrs[-1][1]) else attrs[-1][1][:-22]
                self.team_2.append(team_2)
                self.GAMES[-1].team_2 = team_2
                self.team_2_flag = False
            else:
                self.flag_flag = False

    def handle_data(self, data):
        if self.time_flag:
            data = data.strip()
#            print("HERE time")
#            print("TIME: ", data)
            self.time.append(data)
            self.GAMES[-1].time = data
#            self.GAMES[-1].live = self.is_live(data)
            self.time_flag = False

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
            if (attrs == [("class", "flag")]):
                self.flag_flag = True
            elif (attrs == [("class", "team-right")]):
                self.team_2_flag = True
            elif ("class", "timer-object timer-object-countdown-only") in attrs:
                self.time_flag = True
            self.handle_game_data(tag, attrs)
#        if self.tagStack: print(self.tagStack)           # PRINT MAIN tagStack

    def handle_endtag(self, endTag):
        if (self.tagStack) and (endTag == self.tagStack[-1]):
            self.tagStack.pop()



def main():
    tournaments = MainPageParser(AOE_liquipedia_URL)
    for tour in tournaments.TOURNAMENTS:
        if tour.live == "LIVE!":
            print(tour.title,  tour.live, '\n')
            games = TournamentPageParser(tour.link)
            for game in games.GAMES:
                print(game, '\n\n')
        else:
            print(tour.title, tour.live, '\n')

if __name__ == "__main__":
    main()
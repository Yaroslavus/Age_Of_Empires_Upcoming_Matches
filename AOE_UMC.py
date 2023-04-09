# Age Of Empires 2 Upcoming Matches Containers

from urllib.request import urlopen
from html.parser import HTMLParser
from dataclasses import dataclass
import calendar
import re
from datetime import datetime, timedelta


@dataclass
class Tournament:
    tournament_hash_list = iter(range(100, 200))
    tier: str = None
    title: str = None
    date: str = None
    link: str = None
    prize: str = None
    participants_number: str = None
    location: str = None
    start_datetime_local: datetime = None
    finish_datetime_local: datetime = None
    def __hash__(self):
        return next(self.tournament_hash_list)


@dataclass
class Game:
    game_hash_list = iter(range(200, 500))
    team_1: str = None
    team_2: str = None
    stage: str = None
    start_datetime_local: datetime = None
    finish_datetime_local: datetime = None
    def __hash__(self):
        return next(self.game_hash_list)

class MainPageParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        self._tagStack = []
        self.TOURNAMENTS = []
        self.AOE_liquipedia_prefix = "https://liquipedia.net"
        self.AOE_liquipedia_URL = self.AOE_liquipedia_prefix + "/ageofempires/Age_of_Empires_II"
        self._location_flag = False
        self._participants_flag = False
        self._date_flag = False
        self._prize_flag = False
        super().__init__(*args, **kwargs)
        self.feed(self.read_site_content())

    def read_site_content(self):
        return str(urlopen(self.AOE_liquipedia_URL).read())

    def __handle_tourhament_data(self, tag, attrs):
        if (tag == 'a') and (self._tagStack[-2] == 'b'):
            link = self.AOE_liquipedia_prefix + attrs[0][1]
            self.TOURNAMENTS[-1].link = link

        elif (tag == 'a') and attrs and len(attrs) == 2 and (attrs[0][0] == 'href') and (attrs[1][0] == 'title'):
            tier = attrs[1][1].split('/')[-1]
            if (tier == 'S-Tier Tournaments') or (tier == 'A-Tier Tournaments'):
                self.TOURNAMENTS[-1].tier = tier.split()[0]

        elif (tag == 'a') and attrs and len(attrs) == 2 and (attrs[0][0] == 'href') and (attrs[1][0] == 'title'):
            location = attrs[0][1].split("Category:")
            if len(location) == 2:
                self.TOURNAMENTS[-1].location = location[1]

    def __to_local_datetime(self, utc_dt):
        return datetime.fromtimestamp(calendar.timegm(utc_dt.timetuple()))

    def __start_finish_datetime(self, data):
        days = re.findall(re.compile(r'[\s,-](\d{2})[\s,-]'), data)
        days = days if len(days) == 2 else days*2
        years = re.findall(re.compile(r'(\d{4})'), data)
        years = years*2 if len(years) == 1 else years
        monthes = [list(calendar.month_abbr).index(word) for word in data.split() if word in list(calendar.month_abbr)[1:]]
        monthes = monthes*2 if len(monthes) == 1 else monthes
        start_datetime = datetime.strptime(f'{days[0]}.{monthes[0]}.{years[0][2:]}', '%d.%m.%y')
        finish_datetime = datetime.strptime(f'{days[1]}.{monthes[1]}.{years[1][2:]}', '%d.%m.%y')
        start_datetime_local = self.__to_local_datetime(start_datetime)
        finish_datetime_local = self.__to_local_datetime(finish_datetime)
        return start_datetime_local, finish_datetime_local

    def handle_data(self, data):
        if (self._tagStack[-2:] == ['b', 'a']):
            self.TOURNAMENTS[-1].title = data

        if self._date_flag:
            self.TOURNAMENTS[-1].date = data
            self.TOURNAMENTS[-1].start_datetime_local, self.TOURNAMENTS[-1].finish_datetime_local = self.__start_finish_datetime(data)
            self._date_flag = False

        if self._prize_flag:
            self.TOURNAMENTS[-1].prize = data
            self._prize_flag = False

        if self._participants_flag:
            self.TOURNAMENTS[-1].participants_number = data
            self._participants_flag = False

        if self._location_flag:
            self.TOURNAMENTS[-1].location = data
            self._location_flag = False

    def handle_starttag(self, tag, attrs):
        if (not self._tagStack) and (tag == 'div') and (attrs == [("class", "divRow")]):
            self._tagStack = []
            self._tagStack.append(tag)
            tournament = Tournament()
            self.TOURNAMENTS.append(tournament)
        elif (self._tagStack) and (self._tagStack[0] == 'div'):
            self._tagStack.append(tag)
            if (attrs == [("class", "divCell EventDetails Date Header")]):
                self._date_flag = True
            elif (attrs == [("class", "divCell EventDetails Prize Header")]):
                self._prize_flag = True
            elif (attrs == [("class", "divCell EventDetails PlayerNumber Header")]):
                self._participants_flag = True
            elif (attrs == [("class", "divCell EventDetails Location Header")]):
                self._location_flag = True
            self.__handle_tourhament_data(tag, attrs)

    def handle_endtag(self, endTag):
        if (self._tagStack) and (endTag == self._tagStack[-1]):
            self._tagStack.pop()


class TournamentPageParser(HTMLParser):
    def __init__(self, site_name, *args, **kwargs):
        self._tagStack = []
        self.GAMES = []
        self._team_1_flag = False
        self._team_2_flag = False
        self._time_flag = False
        self._stage_flag = False
        self._flag_flag = False
        self.site_name = site_name
        super().__init__(*args, **kwargs)
        self.feed(self.__read_site_content())

    def __read_site_content(self):
        return str(urlopen(self.site_name).read())

    def __to_local_datetime(self, utc_dt):
        return datetime.fromtimestamp(calendar.timegm(utc_dt.timetuple()))

    def __start_finish_datetime(self, data):
        days = re.findall(re.compile(r'[\s,-](\d{2})[\s,-]'), data)
        years = re.findall(re.compile(r'(\d{4})'), data)
        monthes = [list(calendar.month_abbr).index(word[:3]) for word in data.split() if word[:3] in list(calendar.month_abbr)[1:]]
        time = re.findall(re.compile(r'(\d{2}:\d{2})'), data)[0]
        hours, minutes = time.split(":")
        start_datetime = datetime.strptime(f'{days[0]}.{monthes[0]}.{years[0][2:]}.{hours}.{minutes}', '%d.%m.%y.%H.%M')
        start_datetime_local = self.__to_local_datetime(start_datetime)
        finish_datetime_local = self.__to_local_datetime(start_datetime) + timedelta(0, 0, 0, 0, 0, 4, 0)
        return start_datetime_local, finish_datetime_local

    def __handle_game_data(self, tag, attrs):
        if self._team_1_flag and (tag == 'a') and attrs and (attrs[0][0] == 'href') and (attrs[-1][0] == 'title'):
            if not (self._flag_flag):
                team_1 = attrs[-1][1] if ('(page does not exist)' not in attrs[-1][1]) else attrs[-1][1][:-22]
                self.GAMES[-1].team_1 = team_1
                self._team_1_flag = False
            else:
                self._flag_flag = False
        elif self._team_1_flag and (tag == 'abbr') and attrs and attrs == [("title", "To Be Determined")]:
            if not (self._flag_flag):
                team_1 = attrs[0][1]
                self.GAMES[-1].team_1 = team_1
                self._team_1_flag = False
            else:
                self._flag_flag = False

        if self._team_2_flag and (tag == 'a') and attrs and (attrs[0][0] == 'href') and (attrs[-1][0] == 'title'):
            if not (self._flag_flag):
                team_2 = attrs[-1][1] if ('(page does not exist)' not in attrs[-1][1]) else attrs[-1][1][:-22]
                self.GAMES[-1].team_2 = team_2
                self._team_2_flag = False
            else:
                self._flag_flag = False
        elif self._team_2_flag and (tag == 'abbr') and attrs and attrs == [("title", "To Be Determined")]:
            if not (self._flag_flag):
                team_2 = attrs[0][1]
                self.GAMES[-1].team_2 = team_2
                self._team_2_flag = False
            else:
                self._flag_flag = False

    def handle_data(self, data):
        if self._time_flag:
            data = data.strip()
            self.GAMES[-1].start_datetime_local, self.GAMES[-1].finish_datetime_local = self.__start_finish_datetime(data)
            self._time_flag = False
        else:
            if self.GAMES and self.GAMES[-1].team_1 and self.GAMES[-1].team_2 and not self.GAMES[-1].stage:
                possible_stages = ["round of 32", "round of 16", "playoffs", "finals",
                                   "semifinals", "quaterfinals", "double elimination stage",
                                   "single-elimination stage", "group stage"]
                if data.lower() in possible_stages:
                    self.GAMES[-1].stage = data

    def handle_starttag(self, tag, attrs):
        if (not self._tagStack) and (tag == 'table') and (attrs == [("class", "wikitable wikitable-striped infobox_matches_content")]):
            self._tagStack = []
            self._tagStack.append(tag)
            game = Game()
            self.GAMES.append(game)
        elif (self._tagStack) and (self._tagStack[0] == 'table'):
            self._tagStack.append(tag)

            if (attrs == [("class", "team-left")]):
                self._team_1_flag = True
            if (attrs == [("class", "flag")]):
                self._flag_flag = True
            elif (attrs == [("class", "team-right")]):
                self._team_2_flag = True
            elif ("class", "timer-object timer-object-countdown-only") in attrs:
                self._time_flag = True
            self.__handle_game_data(tag, attrs)

    def handle_endtag(self, endTag):
        if (self._tagStack) and (endTag == self._tagStack[-1]):
            self._tagStack.pop()


class MainContainerManager:
    def __init__(self, tournaments):
        self.tournaments = tournaments
        self.all_tournaments_dict, self.nearest_object = self.__get_main_containers()

    def __get_main_containers(self):
        all_tournaments_dict = {}
        infinity_future = datetime(2100, 1, 1, 0, 0, 0)
        nearest_object = Game(start_datetime_local = infinity_future)
        time_now = datetime.now()
        for tournament in self.tournaments.TOURNAMENTS:
            if tournament.finish_datetime_local > datetime.now():
                games = TournamentPageParser(tournament.link)
                all_tournaments_dict[tournament] = games.GAMES
                for game in games.GAMES:
                    if (game.start_datetime_local < nearest_object.start_datetime_local) and (game.start_datetime_local > time_now):
                        nearest_object = game
                if (tournament.start_datetime_local < nearest_object.start_datetime_local) and (tournament.start_datetime_local > time_now):
                    nearest_object = tournament
        return all_tournaments_dict, nearest_object
from urllib.request import urlopen
from html.parser import HTMLParser
from calendar import month_abbr
from collections import namedtuple

AOE_liquipedia_URL = """https://liquipedia.net/ageofempires/Age_of_Empires_II"""


class MyHTMLParser(HTMLParser):

    def __init__(self, site_name, *args, **kwargs):
        self.tagStack = []
#        self.TOURNAMENTS = []
#        self.Tournament = namedtuple("tier", "title", "date", "link",
#                                "prize", "part_number", "location",
#                                defaults=(None))
        self.tiers, self.titles, self.dates, self.links = [], [], [], []
        self.prizes, self.participants, self.locations = [], [], []
        self.site_name = site_name
        super().__init__(*args, **kwargs)
        self.feed(self.read_site_content())

    def read_site_content(self):
        return str(urlopen(self.site_name).read())

    def handle_tourhament_data(self, tag, attrs):
        if (tag == 'a') and (self.tagStack[-2] == 'b'):
            link = "https://liquipedia.net" + attrs[0][1]
            self.links.append(link)

        elif (tag == 'a') and attrs and len(attrs) == 2 and (attrs[0][0] == 'href') and (attrs[1][0] == 'title'):
            tier = attrs[1][1].split('/')[-1]
            if (tier == 'S-Tier Tournaments') or (tier == 'A-Tier Tournaments'):
                self.tiers.append(tier.split()[0])

    def handle_data(self, data):
        if (self.tagStack[-2:] == ['b', 'a']):
            self.titles.append(data)
        print(f'HERE :::{data}:::')
        if (data) and (data not in ['\t', '\n', '\v', '\r', '\f', ' ']) and (data.split()[0] in month_abbr[1:]):
            self.dates.append(data)
        if (data[0] == '$'):
            self.prizes.append(data)

    def handle_starttag(self, tag, attrs):
        if (not self.tagStack) and (tag == 'div') and (attrs == [("class", "divRow")]):
            self.tagStack = []
            self.tagStack.append(tag)
#            self.TOURNAMENTS.append(self.Tournament())
        elif (self.tagStack) and (self.tagStack[0] == 'div'):
            self.tagStack.append(tag)
            self.handle_tourhament_data(tag, attrs)
#        if self.tagStack: print(self.tagStack)           # PRINT MAIN tagStack

    def handle_endtag(self, endTag):
        if (self.tagStack) and (endTag == self.tagStack[-1]):
            self.tagStack.pop()


def parse_via_re(URL):
    import re

    LIST_OF_TOURNAMENTS_PATTERN = """<div class="divTable table-full-width tournament-card">.*Game and Series.*<\/div><\/div><\/div>"""
    TORNAMENT_TIER_PATTERN = """Tournaments">(.-Tier)"""
    LINK_AND_NAME_PATTERN = """<a href="(\/ageofempires\/[a-zA-Z0-9_\/#%$@&;':.,?)(*^!]+)" title="[a-zA-Z0-9_\/ #%$@&;':.,?)(*^!]+">([a-zA-Z0-9_\/ #%$@&;':.,?)(*^!]+)<\/a><\/b><\/div>"""
    DATE_PATTERN = """Date Header">([a-zA-Z0-9, -]+)"""
    PRIZE_PATTERN = """Prize Header">([a-zA-Z0-9, -$]+)"""
    PARTICIPANTS_NUMBER_PATTERN = """PlayerNumber Header">([0-9]+)"""
    LOCATION_PATTERN = """<\/span>&#160;([a-zA-Z0-9]+)"""

    liquipedia_main_content = str(urlopen(URL).read())

    tournaments_raw_string = re.findall(LIST_OF_TOURNAMENTS_PATTERN, liquipedia_main_content)[0]
    tournaments_type = re.findall(TORNAMENT_TIER_PATTERN, tournaments_raw_string)
    tournaments_link_and_name = re.findall(LINK_AND_NAME_PATTERN, tournaments_raw_string)
    tournaments_link = [x[0] for x in tournaments_link_and_name]
    tournaments_name = [x[1] for x in tournaments_link_and_name]
    tournaments_date = re.findall(DATE_PATTERN, tournaments_raw_string)
    tournaments_prize = re.findall(PRIZE_PATTERN, tournaments_raw_string)
    tournaments_participants_number = re.findall(PARTICIPANTS_NUMBER_PATTERN, tournaments_raw_string)
    tournaments_location = re.findall(LOCATION_PATTERN, tournaments_raw_string)
    parsed_content = [tournaments_type, tournaments_link, tournaments_name,
                      tournaments_date, tournaments_prize,
                      tournaments_participants_number, tournaments_location]

    base_length = len(tournaments_type)
    assert all([len(item) == base_length for item in parsed_content]), "Maybe some fields didn't parsed fine!"

    tournaments = list(zip(*parsed_content))

    return tournaments


def main():
    tournaments = MyHTMLParser(AOE_liquipedia_URL)
    print(len(tournaments.tiers), tournaments.tiers, '\n')
    print(len(tournaments.links), tournaments.links, '\n')
    print(len(tournaments.titles), tournaments.titles, '\n')
    print(len(tournaments.prizes), tournaments.prizes, '\n')
    print(len(tournaments.dates), tournaments.dates, '\n')
    print(len(tournaments.participants), tournaments.participants, '\n')
    print(len(tournaments.locations), tournaments.locations, '\n')

#    for x in tournaments_list:
#        print(x, '\n\n')

if __name__ == "__main__":
    main()
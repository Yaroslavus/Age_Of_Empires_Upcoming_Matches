import tkinter as tk
from datetime import datetime
from tkinter.messagebox import askyesno
import AOE_UMC
import webbrowser
import tkinter.font as tkFont
# hi

class UpcomingMatchesViewer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Age Of Empires 2 Upcoming Matches")
        self.time_to_next_refresh = float("inf")
        self.main_frame = tk.LabelFrame(self, text="Age Of Empires 2 Upcoming Matches", bd=2)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.head_frame = tk.Frame(self.main_frame, bd=0)
        self.head_frame.pack(fill="x", padx=10, pady=10)
        self.__set_head_frame()
        self.upcoming_tournaments_frame = tk.LabelFrame(self.main_frame, text="Upcoming tournaments", bd=2)
        self.upcoming_tournaments_frame.pack(fill="both", expand=False, padx=10, pady=10)
        self.live_tournaments_frame = tk.LabelFrame(self.main_frame, text="Live tournaments", bd=2)
        self.live_tournaments_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.__large_period_refresh()

    def __set_head_frame(self):
        self.refresh_button = tk.Button(self.head_frame, text="Refresh all Information (takes about 30 sec)", command=lambda: self.__manual_refresh())
        self.main_URL_label = tk.Label(self.head_frame, text="Main tornaments", cursor="hand2")
        self.__Label_to_URL(self.main_URL_label, "https://liquipedia.net/ageofempires/Age_of_Empires_II")
        self.even_more_main_URL_label = tk.Label(self.head_frame, text="Even more tornaments", cursor="hand2")
        self.__Label_to_URL(self.even_more_main_URL_label, "https://liquipedia.net/ageofempires/Age_of_Empires_II/Tournaments/Post_2020")
        for object in (self.refresh_button, self.main_URL_label, self.even_more_main_URL_label):
            object.pack(side="left", padx=10, pady=10)
        self.clock_label = tk.Label(self.head_frame, text="", anchor='e')
        self.clock_label.pack(side="right", padx=10, pady=10)

    def __manual_refresh(self):
        if askyesno(title="Full Refreshing", message="Do you really want to refresh the form?"):
            self.__full_refresh()

    def __full_refresh(self):
        self.clock_label.destroy()
        self.upcoming_tournaments_frame.destroy()
        self.live_tournaments_frame.destroy()
        self.clock_label = tk.Label(self.head_frame, text = datetime.now().strftime("%d.%m.%y  %H:%M:%S"))
        self.clock_label.pack(side="right", padx=10, pady=10)
        self.upcoming_tournaments_frame = tk.LabelFrame(self.main_frame, text="Upcoming tournaments")
        self.upcoming_tournaments_frame.pack(fill="both", expand=False, padx=10, pady=10)
        self.live_tournaments_frame = tk.LabelFrame(self.main_frame, text="Live tournaments")
        self.live_tournaments_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_container = AOE_UMC.MainContainerManager(AOE_UMC.MainPageParser())
        self.time_to_next_refresh = int((self.main_container.nearest_object.start_datetime_local - datetime.now()).total_seconds())
        self.countdown_upcoming_tournaments_labels = []
        self.countdown_upcoming_tournaments = []
        self.countdown_games_labels = []
        self.countdown_games = []
        self.__fill_upcoming_tournaments()
        self.__fill_live_tournaments()
        self.__small_period_refresh()

    def __large_period_refresh(self):
        self.after(min(12*3600000, self.time_to_next_refresh*1000), self.__large_period_refresh)
        self.__full_refresh()

    def __small_period_refresh(self):
        self.after(1000, self.__small_period_refresh)
        for game, countdown_label in list(zip(self.countdown_games, self.countdown_games_labels)):
            if (self.__activity_status(game, 1) == "LIVE!") and (countdown_label.cget("text") != "LIVE!"):
                countdown_label.config(text = "LIVE!")
                countdown_label.config(bg="red")
            elif self.__activity_status(game, 1)  == "Soon":
                timedelta = self.__td_format(game.start_datetime_local - datetime.now())
                countdown_label.config(text = f'{timedelta}')
        for upcoming_tournament, upcoming_tournament_countdown_label in list(zip(self.countdown_upcoming_tournaments, self.countdown_upcoming_tournaments_labels)):
                timedelta = self.__td_format(upcoming_tournament.start_datetime_local - datetime.now())
                upcoming_tournament_countdown_label.config(text = f'{timedelta}')
        self.clock_label.config(text = datetime.now().strftime("%d.%m.%y  %H:%M:%S"))

    def __fill_upcoming_tournaments(self):
        self.upcoming_tournaments_frame.columnconfigure(index=0, weight=2)
        for c in range(1, 7): self.upcoming_tournaments_frame.columnconfigure(index=c, weight=1)
        upcoming_tournaments_counter = 0
        for row, tournament in enumerate(self.main_container.all_tournaments_dict.keys()):
            if self.__activity_status(tournament, 0) == "Soon":
                self.countdown_upcoming_tournaments.append(tournament)
                upcoming_tournaments_counter += 1
                if upcoming_tournaments_counter == 1:
                    title_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Title", bd=0)
                    tier_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Tier", bd=0)
                    start_time_local_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Local Start Date", bd=0)
                    timedelta_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Time to start", bd=0)
                    prize_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Prize", bd=0)
                    participants_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Participants Number", bd=0)
                    location_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Location", bd=0)
                    for i, frame in enumerate(iter([title_frame, tier_frame, start_time_local_frame,
                                                    timedelta_frame, prize_frame, participants_frame,
                                                    location_frame])):
                        frame.grid(row=row, column=i, padx=20, sticky='nw')
                start_time_local = tournament.start_datetime_local.strftime("%d.%m.%y")
                timedelta = self.__td_format(tournament.start_datetime_local - datetime.now())
                tournament_title = tk.Label(title_frame, text=f'{tournament.title}', cursor="hand2")
                self.__Label_to_URL(tournament_title, tournament.link)
                tournament_tier = tk.Label(tier_frame, text=f'{tournament.tier}')
                tournament_start_time_local = tk.Label(start_time_local_frame, text=f'{start_time_local}')
                tournament_date = tk.Label(timedelta_frame, text=f'{timedelta}')
                self.countdown_upcoming_tournaments_labels.append(tournament_date)
                tournament_prize = tk.Label(prize_frame, text=f'{tournament.prize}')
                tournament_participants_number = tk.Label(participants_frame, text=f'{tournament.participants_number}')
                tournament_location = tk.Label(location_frame, text=f'{tournament.location}')
                for i, label in enumerate(iter([tournament_title, tournament_tier, tournament_start_time_local,
                                                tournament_date, tournament_prize, tournament_participants_number,
                                                tournament_location])):
                        label.grid(row=row, column=i, padx=10, sticky='nw')
        if not upcoming_tournaments_counter:
            self.no_upcoming_tours_label = tk.Label(self.upcoming_tournaments_frame, text="There are no any upcoming tournaments.")
            self.no_upcoming_tours_label.pack(side="left", fill="x", padx=10)

    def __fill_live_tournaments(self):
        live_tournaments_counter = 0
        for tournament, games_list in self.main_container.all_tournaments_dict.items():
            if self.__activity_status(tournament, 0) == "LIVE!":
                live_tournament_frame = tk.LabelFrame(self.live_tournaments_frame, text=f'{tournament.title}\t{tournament.date}\t{tournament.tier}', bd=2, cursor="hand2")
                live_tournament_frame.pack(fill="both", expand=True, padx=20, pady=10)
                self.__Label_to_URL(live_tournament_frame, tournament.link)
                live_tournaments_counter += 1
                self.__fill_live_tournament_with_games(games_list, live_tournament_frame)
        if not live_tournaments_counter:
            self.no_live_tours_label = tk.Label(self.live_tournaments_frame, text="There are no any live tournaments.")
            self.no_live_tours_label.grid(row=0, column=0, padx=10, sticky="w")

    def __fill_live_tournament_with_games(self, games_list, live_tournament_frame):
        game_counter = 0
        for game in games_list:
            start_time_local = game.start_datetime_local.strftime("%d.%m.%y %H:%M")
            game_counter += 1
            if game_counter == 1:
                for c in range(4): live_tournament_frame.columnconfigure(index=c, weight=1, uniform="group1")
                teams_frame = tk.LabelFrame(live_tournament_frame, text="Game", bd=0)
                start_time_local_frame = tk.LabelFrame(live_tournament_frame, text="Local Start Time", bd=0)
                activity_status_frame = tk.LabelFrame(live_tournament_frame, text="Activity Status", bd=0)
                stage_frame = tk.LabelFrame(live_tournament_frame, text="Stage", bd=0)
                for i, frame in enumerate(iter([teams_frame, start_time_local_frame,
                                                activity_status_frame, stage_frame])):
                        frame.grid(row=0, column=i, padx=20, pady=10, sticky='nesw')
            game_title = tk.Label(teams_frame, text=f'{game.team_1} vs. {game.team_2}')
            game_time = tk.Label(start_time_local_frame, text=f'{start_time_local}')
            game_stage = tk.Label(stage_frame, text=f'{game.stage}')
            for label in (game_title, game_time, game_stage):
                label.pack(padx=10, anchor='nw')
            if self.__activity_status(game, 1)  == "LIVE!":
                game_activity_status = tk.Label(activity_status_frame, text="LIVE!", bg='red')
                game_activity_status.pack(padx=10, anchor='nw')
            elif self.__activity_status(game, 1)  == "Soon":
                timedelta = self.__td_format(game.start_datetime_local - datetime.now())
                game_activity_status = tk.Label(activity_status_frame, text=f'{timedelta}', bg='lightblue')
                game_activity_status.pack(padx=10, anchor='nw')
                self.countdown_games.append(game)
                self.countdown_games_labels.append(game_activity_status)
        if not game_counter:
            self.no_live_games_label = tk.Label(live_tournament_frame, text="There are no any upcoming or live games.")
            self.no_live_games_label.grid(row=0, column=0, padx=10, sticky="w")

    def __td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [('year', 60*60*24*365), ('month', 60*60*24*30),
                   ('day', 60*60*24), ('hour', 60*60), ('minute', 60)]
        strings = []
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append("%s %s%s" % (period_value, period_name, has_s))
        return ", ".join(strings)

    def __activity_status(self, object, game_flag=1):
        now = datetime.now()
        if (now >= object.start_datetime_local) and (now <= object.finish_datetime_local):
            return "LIVE!"
        elif (now < object.start_datetime_local):
            return "Soon"
        elif (now > object.finish_datetime_local):
            return "Started more than 4 hours ago" if game_flag else "Finished"

    def __callback(self, url):
        webbrowser.open_new_tab(url)

    def __underline(self, widget, underline):
        f = tkFont.Font(widget, widget.cget("font"))
        f.configure(underline = underline)
        widget.configure(font=f)

    def __Label_to_URL(self, widget, link):
        widget.bind("<Button-1>", lambda e: self.__callback(link))
        widget.bind("<Enter>", lambda e: self.__underline(widget, underline=True))
        widget.bind("<Leave>", lambda e: self.__underline(widget, underline=False))


if __name__ == "__main__":
    UpcomingMatchesViewer().mainloop()
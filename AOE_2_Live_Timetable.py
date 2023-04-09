import tkinter as tk
from datetime import datetime, timedelta
from tkinter.messagebox import askyesno
import AOE_UMC


class UpcomingMatchesViewer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.master_frames_border_width = 2
        self.slave_frames_border_width = 0
        self.time_to_next_refresh = float("inf")
        self.winfo_toplevel().title("Age Of Empires 2 Upcoming Matches")
        self.main_frame = tk.LabelFrame(self, text="Age Of Empires 2 Upcoming Matches", bd=self.master_frames_border_width)
        self.main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.refresh_button = tk.Button(self.main_frame, text="Refresh all Information (takes about 30 sec)", command=lambda: self.__manual_refresh())
        self.refresh_button.pack(side="top", padx=10, pady=10, anchor='nw')
        self.upcoming_tournaments_frame = tk.LabelFrame(self.main_frame, text="Upcoming tournaments", bd=self.master_frames_border_width)
        self.upcoming_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.live_tournaments_frame = tk.LabelFrame(self.main_frame, text="Live tournaments", bd=self.master_frames_border_width)
        self.live_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10)
#        self.finished_tournaments_frame = tk.LabelFrame(self.main_frame, text="Finished tournaments", bd=self.master_frames_border_width)
#        self.finished_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.__large_period_refresh()

    def __manual_refresh(self):
        if askyesno(title="Full Refreshing", message="Do you really want to refresh the form?"):
            self.__full_refresh()

    def __full_refresh(self):
        self.upcoming_tournaments_frame.destroy()
        self.live_tournaments_frame.destroy()
        self.upcoming_tournaments_frame = tk.LabelFrame(self.main_frame, text="Upcoming tournaments")
        self.upcoming_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.live_tournaments_frame = tk.LabelFrame(self.main_frame, text="Live tournaments")
        self.live_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10)
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

    def __fill_upcoming_tournaments(self):
        upcoming_tournaments_counter = 0
        for row, tournament in enumerate(self.main_container.all_tournaments_dict.keys()):
            if self.__activity_status(tournament, 0) == "Soon":
                self.countdown_upcoming_tournaments.append(tournament)
                upcoming_tournaments_counter += 1
                if upcoming_tournaments_counter == 1:
                    # TODO: Later we will play with borders and fonts:
                    # title_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Title", font= ('Helvetica 14 bold'), bd= 0)
                    title_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Title", bd=self.slave_frames_border_width)
                    tier_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Tier", bd=self.slave_frames_border_width)
                    start_time_local_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Local Start Date", bd=self.slave_frames_border_width)
                    timedelta_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Time to start", bd=self.slave_frames_border_width)
                    prize_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Prize", bd=self.slave_frames_border_width)
                    participants_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Participants Number", bd=self.slave_frames_border_width)
                    location_frame = tk.LabelFrame(self.upcoming_tournaments_frame, text="Location", bd=self.slave_frames_border_width)
                    title_frame.pack(side="left", fill="both", expand=True, padx=20)
                    tier_frame.pack(side="left", fill="both", expand=True, padx=10)
                    start_time_local_frame.pack(side="left", fill="both", expand=True, padx=10)
                    timedelta_frame.pack(side="left", fill="both", expand=True, padx=10)
                    prize_frame.pack(side="left", fill="both", expand=True, padx=10)
                    participants_frame.pack(side="left", fill="both", expand=True, padx=10)
                    location_frame.pack(side="left", fill="both", expand=True, padx=10)
                start_time_local = tournament.start_datetime_local.strftime("%d.%m.%y")
                timedelta = self.__td_format(tournament.start_datetime_local - datetime.now(), game_flag=0)
                tournament_title = tk.Label(title_frame, text=f'{tournament.title}')
                tournament_tier = tk.Label(tier_frame, text=f'{tournament.tier}')
                tournament_start_time_local = tk.Label(start_time_local_frame, text=f'{start_time_local}')
                tournament_date = tk.Label(timedelta_frame, text=f'{timedelta}')
                self.countdown_upcoming_tournaments_labels.append(tournament_date)
                tournament_prize = tk.Label(prize_frame, text=f'{tournament.prize}')
                tournament_participants_number = tk.Label(participants_frame, text=f'{tournament.participants_number}')
                tournament_location = tk.Label(location_frame, text=f'{tournament.location}')
                tournament_title.pack(side="top", anchor="w")
                tournament_tier.pack(side="top", anchor="w")
                tournament_start_time_local.pack(side="top", anchor="w")
                tournament_date.pack(side="top", anchor="w")
                tournament_prize.pack(side="top", anchor="w")
                tournament_participants_number.pack(side="top", anchor="w")
                tournament_location.pack(side="top", anchor="w")
        if not upcoming_tournaments_counter:
            self.no_upcoming_tours_label = tk.Label(self.upcoming_tournaments_frame, text="There are no any upcoming tournaments.")
            self.no_upcoming_tours_label.pack(side="left", anchor="w")

    def __fill_live_tournaments(self):
#        live_tournaments_frames = []
        live_tournaments_counter = 0
        for row, (tournament, games_list) in enumerate(self.main_container.all_tournaments_dict.items()):
            if self.__activity_status(tournament, 0) == "LIVE!":
                live_tournament_frame = tk.LabelFrame(self.live_tournaments_frame, text=f'{tournament.title}\t{tournament.date}\t{tournament.tier}', bd=self.master_frames_border_width)
                live_tournament_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)
                live_tournaments_counter += 1
#                live_tournaments_frames.append(live_tournament_frame)
                self.__fill_live_tournament_with_games(games_list, live_tournament_frame)
        if not live_tournaments_counter:
            self.no_live_tours_label = tk.Label(self.live_tournaments_frame, text="There are no any live tournaments.")
            self.no_upcoming_tours_label.pack(side="left", anchor="w")

    def __fill_live_tournament_with_games(self, games_list, live_tournament_frame):
        game_counter = 0
        tournament_frame_width = live_tournament_frame.winfo_width()
        for row, game in enumerate(games_list):
            start_time_local = game.start_datetime_local.strftime("%d.%m.%y %H:%M")
            game_counter += 1
            if game_counter == 1:
                teams_frame = tk.LabelFrame(live_tournament_frame, text="Game", width=tournament_frame_width/4, bd=self.slave_frames_border_width)
                start_time_local_frame = tk.LabelFrame(live_tournament_frame, text="Local Start Time", width=tournament_frame_width/4, bd=self.slave_frames_border_width)
                activity_status_frame = tk.LabelFrame(live_tournament_frame, text="Activity Status", width=tournament_frame_width/4, bd=self.slave_frames_border_width)
                stage_frame = tk.LabelFrame(live_tournament_frame, text="Stage", width=tournament_frame_width/4, bd=self.slave_frames_border_width)
                teams_frame.pack(side="left", fill="both", expand=True, padx=20)
                start_time_local_frame.pack(side="left", fill="both", expand=True, padx=10)
                activity_status_frame.pack(side="left", fill="both", expand=True, padx=10)
                stage_frame.pack(side="left", fill="both", expand=True, padx=10)
            game_title = tk.Label(teams_frame, text=f'{game.team_1} vs. {game.team_2}')
            game_time = tk.Label(start_time_local_frame, text=f'{start_time_local}')
            game_stage = tk.Label(stage_frame, text=f'{game.stage}')
            game_title.pack(side="top", anchor="w")
            game_time.pack(side="top", anchor="w")
            game_stage.pack(side="top", anchor="w")
            if self.__activity_status(game, 1)  == "LIVE!":
                game_activity_status = tk.Label(activity_status_frame, text="LIVE!", bg='red')
                game_activity_status.pack(side="top", anchor="w")
            elif self.__activity_status(game, 1)  == "Soon":
                timedelta = self.__td_format(game.start_datetime_local - datetime.now())
                game_activity_status = tk.Label(activity_status_frame, text=f'{timedelta}', bg='lightblue')
                game_activity_status.pack(side="top", anchor="w")
                self.countdown_games.append(game)
                self.countdown_games_labels.append(game_activity_status)
        if not game_counter:
            self.no_live_games_label = tk.Label(live_tournament_frame, text="There are no any upcoming or live games.")
            self.no_live_games_label.pack(side="left", anchor="w")

    def __td_format(self, td_object, game_flag=1):
        seconds = int(td_object.total_seconds())
        periods = [('year', 60*60*24*365), ('month', 60*60*24*30),
                   ('day', 60*60*24), ('hour', 60*60), ('minute', 60), ('second', 1)]

        strings = []
#        periods = periods if game_flag else periods[:-3]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append("%s %s%s" % (period_value, period_name, has_s))
        return ", ".join(strings)

    def __activity_status(self, object, game_flag=1):
        now = datetime.now()
        if (now > object.start_datetime_local) and (now < object.finish_datetime_local):
            return "LIVE!"
        elif (now < object.start_datetime_local):
            return "Soon"
        elif (now > object.finish_datetime_local):
            return "Started more than 4 hours ago" if game_flag else "Finished"


if __name__ == "__main__":
    UpcomingMatchesViewer().mainloop()
#    import cProfile, pstats
#    cProfile.run("UpcomingMatchesViewer().mainloop()", "{}.profile".format(__file__))
#    s = pstats.Stats("{}.profile".format(__file__))
#    s.strip_dirs()
#    s.sort_stats("time").print_stats(10)
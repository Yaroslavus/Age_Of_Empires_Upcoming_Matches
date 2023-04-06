import tkinter as tk
from datetime import datetime, timedelta
from tkinter.messagebox import askyesno
import AOE_UMC


class UpcomingMatchesViewer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Age Of Empires 2 Upcoming Matches")
        self.main_frame = tk.LabelFrame(self, text="Age Of Empires 2 Upcoming Matches")
        self.main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.refresh_button = tk.Button(self.main_frame, text="Refresh all Information (takes about 30 sec)", command=lambda: self.__manual_refresh())
        self.refresh_button.pack(side="top", padx=10, pady=10, anchor='nw')
        self.upcoming_tournaments_frame = tk.LabelFrame(self.main_frame, text="Upcoming tournaments")
        self.upcoming_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.live_tournaments_frame = tk.LabelFrame(self.main_frame, text="Live tournaments")
        self.live_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10)
        self.__timed_refresh()

    def __manual_refresh(self):
        if askyesno(title="Full Refreshing", message="Do you really want to refresh the form?"):
            self.__refresh()

    def __refresh(self):
        self.upcoming_tournaments_frame.destroy()
        self.live_tournaments_frame.destroy()
        self.upcoming_tournaments_frame = tk.LabelFrame(self.main_frame, text="Upcoming tournaments")
        self.upcoming_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.live_tournaments_frame = tk.LabelFrame(self.main_frame, text="Live tournaments")
        self.live_tournaments_frame.pack(side="top", fill="both", expand=True, padx=10)
        self.main_container = AOE_UMC.MainContainerManager(AOE_UMC.MainPageParser())
        self.__fill_upcoming_tournaments()
        self.__fill_live_tournaments()

    def __timed_refresh(self):
        self.after(60000, self.__timed_refresh)
        self.__refresh()

    def __fill_upcoming_tournaments(self):
        upcoming_tournaments_iterator = 0
        for row, tournament in enumerate(self.main_container.all_tournaments_dict.keys()):
            if self.__activity_status(tournament, 0) == "Soon":
                start_time_local = tournament.start_datetime_local.strftime("%d.%m.%y")
                timedelta = self.__td_format(tournament.start_datetime_local - datetime.now(), game_flag=0)
                tournament_title = tk.Label(self.upcoming_tournaments_frame, text=f'{tournament.title}\t{tournament.tier}', anchor="w")
                tournament_tier = tk.Label(self.upcoming_tournaments_frame, text=f'{start_time_local}', anchor="w")
                tournament_date = tk.Label(self.upcoming_tournaments_frame, text=f'{timedelta}', anchor="w")
                tournament_title.grid(row=row, column=0, sticky="ew")
                tournament_tier.grid(row=row, column=2, sticky="ew")
                tournament_date.grid(row=row, column=3, sticky="ew")
                upcoming_tournaments_iterator += 1
        if not upcoming_tournaments_iterator:
            self.no_upcoming_tours_label = tk.Label(self.upcoming_tournaments_frame, text="There are no any upcoming tournaments.")
            self.no_upcoming_tours_label.grid(row=0, column=0, sticky='nsew')

    def __fill_live_tournaments(self):
        live_tournaments_frames = []
        live_tournaments_iterator = 0
        for row, (tournament, games_list) in enumerate(self.main_container.all_tournaments_dict.items()):
            if self.__activity_status(tournament, 0) == "LIVE!":
                live_tournament_frame = tk.LabelFrame(self.live_tournaments_frame, text=f'{tournament.title}\t{tournament.date}\t{tournament.tier}')
                live_tournament_frame.grid(row=row, column=0, sticky='nsew')
                live_tournaments_iterator += 1
                live_tournaments_frames.append(live_tournament_frame)
                self.__fill_live_tournament_with_games(games_list, live_tournament_frame)
        if not live_tournaments_iterator:
            self.no_live_tours_label = tk.Label(self.live_tournaments_frame, text="There are no any live tournaments.")
            self.no_live_tours_label.grid(row=0, column=0, sticky='nsew')

    def __fill_live_tournament_with_games(self, games_list, live_tournament_frame):
        game_iterator = 0
        for row, game in enumerate(games_list):
            start_time_local = game.start_datetime_local.strftime("%d.%m.%y %H:%M")
            if self.__activity_status(game, 1)  == "LIVE!":
                game_title = tk.Label(live_tournament_frame, text=f'{game.team_1} vs. {game.team_2}', anchor="w")
                game_time = tk.Label(live_tournament_frame, text=f'{start_time_local}', anchor="w")
                game_activity_status = tk.Label(live_tournament_frame, text="LIVE!", anchor="w", bg='red')
                game_stage = tk.Label(live_tournament_frame, text=f'{game.stage}', anchor="w")
                game_title.grid(row=row, column=1, sticky="ew")
                game_time.grid(row=row, column=2, sticky="ew")
                game_activity_status.grid(row=row, column=3, sticky="ew")
                game_stage.grid(row=row, column=4, sticky="ew")
            elif self.__activity_status(game, 1)  == "Soon":
                timedelta = self.__td_format(game.start_datetime_local - datetime.now())
                game_title = tk.Label(live_tournament_frame, text=f'{game.team_1} vs. {game.team_2}', anchor="w")
                game_time = tk.Label(live_tournament_frame, text=f'{start_time_local}', anchor="w")
                game_activity_status = tk.Label(live_tournament_frame, text=f'{timedelta}', anchor="w", bg='lightblue')
                game_stage = tk.Label(live_tournament_frame, text=f'{game.stage}', anchor="w")
                game_title.grid(row=row, column=1, sticky="ew")
                game_time.grid(row=row, column=2, sticky="ew")
                game_activity_status.grid(row=row, column=3, sticky="ew")
                game_stage.grid(row=row, column=4, sticky="ew")
            game_iterator += 1
        if not game_iterator:
            self.no_live_games_label = tk.Label(live_tournament_frame, text="There are no any live games.")
            self.no_live_games_label.grid(row=0, column=0, sticky='nsew')

    def __td_format(self, td_object, game_flag=1):
        seconds = int(td_object.total_seconds())
        periods = [('year', 60*60*24*365), ('month', 60*60*24*30),
                   ('day', 60*60*24), ('hour', 60*60), ('minute', 60)]

        strings = []
        if game_flag:
            for period_name, period_seconds in periods:
                if seconds > period_seconds:
                    period_value , seconds = divmod(seconds, period_seconds)
                    has_s = 's' if period_value > 1 else ''
                    strings.append("%s %s%s" % (period_value, period_name, has_s))
        else:
            for period_name, period_seconds in periods[:-2]:
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
#    root = tk.Tk()
#    UpcomingMatchesViewer(root).pack(side="top", fill="both", expand=True, padx=10, pady=10)
#    root.mainloop()
    UpcomingMatchesViewer().mainloop()
import tkinter as tk
import AOE_UMC
from datetime import datetime
from colorama import Fore, Style
import time
from tkinter.messagebox import askyesno


class UpcomingMatchesViewer(tk.LabelFrame):
    def __init__(self, *args, **kwargs):
        tk.LabelFrame.__init__(self, text = "Age Of Empires 2 Upcoming Matches", *args, **kwargs)
        self.tournaments = AOE_UMC.MainPageParser()
        self.main_container = AOE_UMC.MainContainerManager(self.tournaments)
        self.row = 0
        self.winfo_toplevel().title("Age Of Empires 2 Upcoming Matches")
        self.grid_columnconfigure(1, weight=1)
        refresh_button = tk.Button(self, text="Refresh all Information (takes about 30 sec)")
        refresh_button.grid(row=0, column=4, sticky="w")
        tk.Label(self, text="Upcoming Tournaments:", anchor="w").grid(row=1, column=0, sticky="ew")
        tk.Label(self).grid(row=2, column=0, sticky="ew", columnspan=4)
        self.row = 3
        self.__fill_upcoming_tournaments()
        tk.Label(self).grid(row=self.row, column=0, sticky="ew", columnspan=4)
        self.row += 1
        tk.Label(self).grid(row=self.row, column=0, sticky="ew", columnspan=4)
        tk.Label(self, text="Live Tournaments:", anchor="w").grid(row=self.row + 1, column=0, sticky="ew")
        tk.Label(self).grid(row=self.row + 2, column=0, sticky="ew", columnspan=4)
        self.row += 3
        tk.Label(self, text="Tournament", anchor="w").grid(row=self.row, column=0, sticky="ew")
        tk.Label(self, text="Game", anchor="w").grid(row=self.row, column=1, sticky="ew")
        tk.Label(self, text="Start Local Time", anchor="w").grid(row=self.row, column=2, sticky="ew")
        tk.Label(self, text="Activity Status", anchor="w").grid(row=self.row, column=3, sticky="ew")
        tk.Label(self, text="Stage", anchor="w").grid(row=self.row, column=4, sticky="ew")
        self.row += 2
        self.__fill_live_tournaments()

    def __activity_status(self, object, game_flag=1):
        now = datetime.now()
        if (now > object.start_datetime_local) and (now < object.finish_datetime_local):
            return "LIVE!"
        elif (now < object.start_datetime_local):
            return "Soon"
        elif (now > object.finish_datetime_local):
            return "Started more than 4 hours ago" if game_flag else "Finished"

    def full_refresh(self):
        if askyesno(title="Full Refreshing", message="Do you really want to refresh the form?"):
            self.update()
#            refresh_label = tk.Label(self, text="Refreshing...", anchor="w")
#            refresh_label.grid(row=0, column=2, sticky="w")
#            time.sleep(2)
#            UpcomingMatchesViewer(root).pack(side="top", fill="both", expand=True, padx=10, pady=10)
#            refresh_label = tk.Label(self, text="Refreshed", anchor="w")
#            refresh_label.grid(row=0, column=2, sticky="w")
#            time.sleep(0.5)
#            tk.Label(self).grid(row=2, column=0, sticky="ew", columnspan=4)
        else:
            pass

    def __fill_upcoming_tournaments(self):
        for tournament in self.main_container.all_tournaments_dict.keys():
            if self.__activity_status(tournament, 0) == "Soon":
                start_time_local = tournament.start_datetime_local.strftime("%d.%m.%y")
                timedelta = self.__td_format(tournament.start_datetime_local - datetime.now(), game_flag=0)
                tournament_title = tk.Label(self, text=f'{tournament.title}\t{tournament.tier}', anchor="w")
                tournament_tier = tk.Label(self, text=f'{start_time_local}', anchor="w")
                tournament_date = tk.Label(self, text=f'{timedelta}', anchor="w")
                tournament_title.grid(row=self.row, column=0, sticky="ew")
                tournament_tier.grid(row=self.row, column=2, sticky="ew")
                tournament_date.grid(row=self.row, column=3, sticky="ew")
        self.row += 1

    def __fill_live_tournaments(self):
        for tournament, games_list in self.main_container.all_tournaments_dict.items():
            if self.__activity_status(tournament, 0) == "LIVE!":
                tournament_title = tk.Label(self, text=tournament.title, anchor="w")
                tournament_tier = tk.Label(self, text=tournament.tier, anchor="w")
                tournament_date = tk.Label(self, text=tournament.date, anchor="w")
                tournament_title.grid(row=self.row, column=0, sticky="ew")
                tournament_tier.grid(row=self.row + 1, column=0, sticky="ew")
                tournament_date.grid(row=self.row + 2, column=0, sticky="ew")
                for game in games_list:
                    start_time_local = game.start_datetime_local.strftime("%d.%m.%y %H:%M")
                    if self.__activity_status(game, 1)  == "LIVE!":
                        game_title = tk.Label(self, text=f'{game.team_1} vs. {game.team_2}', anchor="w")
                        game_time = tk.Label(self, text=f'{start_time_local}', anchor="w")
                        game_activity_status = tk.Label(self, text="LIVE!", anchor="w", bg='red')
                        game_stage = tk.Label(self, text=f'{game.stage}', anchor="w")
                        game_title.grid(row=self.row, column=1, sticky="ew")
                        game_time.grid(row=self.row, column=2, sticky="ew")
                        game_activity_status.grid(row=self.row, column=3, sticky="ew")
                        game_stage.grid(row=self.row, column=4, sticky="ew")
                        self.row += 1
                    elif self.__activity_status(game, 1)  == "Soon":
                        timedelta = self.__td_format(game.start_datetime_local - datetime.now())
                        game_title = tk.Label(self, text=f'{game.team_1} vs. {game.team_2}', anchor="w")
                        game_time = tk.Label(self, text=f'{start_time_local}', anchor="w")
                        game_activity_status = tk.Label(self, text=f'{timedelta}', anchor="w", bg='lightblue')
                        game_stage = tk.Label(self, text=f'{game.stage}', anchor="w")
                        game_title.grid(row=self.row, column=1, sticky="ew")
                        game_time.grid(row=self.row, column=2, sticky="ew")
                        game_activity_status.grid(row=self.row, column=3, sticky="ew")
                        game_stage.grid(row=self.row, column=4, sticky="ew")
                        self.row += 1
                self.row = self.row if len(games_list) >= 3 else self.row + 3
                tk.Label(self).grid(row=self.row, column=0, sticky="ew", columnspan=4)
                self.row += 1

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


if __name__ == "__main__":
    root = tk.Tk()
    UpcomingMatchesViewer(root).pack(side="top", fill="both", expand=True, padx=10, pady=10)
    root.mainloop()
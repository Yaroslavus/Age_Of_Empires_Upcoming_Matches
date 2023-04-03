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
        self.grid_columnconfigure(1, weight=1)
        refresh_checkbox = tk.Checkbutton(self, text="Put on the flag if you really want to make a full refresh", onvalue=True, offvalue=False)
        refresh_checkbox.grid(row=0, column=0, sticky="nsew")
        refresh_button = tk.Button(self, text="Refresh all Information (takes about 30 sec)", command=lambda: self.full_refresh())
        refresh_button.grid(row=0, column=1, sticky="w")
        tk.Label(self, text="Upcoming Tournaments:", anchor="w").grid(row=1, column=0, sticky="ew")
        tk.Label(self).grid(row=2, column=0, sticky="ew", columnspan=4)
        self.row = 3
        self.fill_upcoming_tournaments()
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
        self.fill_live_tournaments()

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
            refresh_label = tk.Label(self, text="Refreshing...", anchor="w")
            refresh_label.grid(row=0, column=2, sticky="w")
            time.sleep(2)
            UpcomingMatchesViewer(root).pack(side="top", fill="both", expand=True, padx=10, pady=10)
            refresh_label = tk.Label(self, text="Refreshed", anchor="w")
            refresh_label.grid(row=0, column=2, sticky="w")
            time.sleep(0.5)
            tk.Label(self).grid(row=2, column=0, sticky="ew", columnspan=4)
        else:
            pass

    def fill_upcoming_tournaments(self):
        for tournament in self.main_container.all_tournaments_dict.keys():
            if self.__activity_status(tournament, 0) == "Soon":
                tournament_title = tk.Label(self, text=tournament.title, anchor="w")
                tournament_tier = tk.Label(self, text=tournament.tier, anchor="w")
                tournament_date = tk.Label(self, text=tournament.date, anchor="w")
                tournament_title.grid(row=self.row, column=0, sticky="ew")
                tournament_tier.grid(row=self.row, column=1, sticky="ew")
                tournament_date.grid(row=self.row, column=2, sticky="ew")
        self.row += 1

    def fill_live_tournaments(self):
        for tournament, games_list in self.main_container.all_tournaments_dict.items():
            if self.__activity_status(tournament, 0) == "LIVE!":
                tournament_title = tk.Label(self, text=tournament.title, anchor="w")
                tournament_tier = tk.Label(self, text=tournament.tier, anchor="w")
                tournament_date = tk.Label(self, text=tournament.date, anchor="w")
                tournament_title.grid(row=self.row, column=0, sticky="ew")
                tournament_tier.grid(row=self.row + 1, column=0, sticky="ew")
                tournament_date.grid(row=self.row + 2, column=0, sticky="ew")
                for game in games_list:
                    if self.__activity_status(game, 1) in ["LIVE!", "Soon"]:
                        game_title = tk.Label(self, text=f'{game.team_1} vs. {game.team_2}', anchor="w")
                        game_time = tk.Label(self, text=f'{game.time}', anchor="w")
                        game_activity_status = tk.Label(self, text=f'{self.__activity_status(game, 1)}', anchor="w")
                        game_stage = tk.Label(self, text=f'{game.stage}', anchor="w")
                        game_title.grid(row=self.row, column=1, sticky="ew")
                        game_time.grid(row=self.row, column=2, sticky="ew")
                        game_activity_status.grid(row=self.row, column=3, sticky="ew")
                        game_stage.grid(row=self.row, column=4, sticky="ew")
                        self.row += 1
                self.row = self.row if len(games_list) >= 3 else self.row + 3
                tk.Label(self).grid(row=self.row, column=0, sticky="ew", columnspan=4)
                self.row += 1


if __name__ == "__main__":
    root = tk.Tk()
    UpcomingMatchesViewer(root).pack(side="top", fill="both", expand=True, padx=10, pady=10)
    root.mainloop()
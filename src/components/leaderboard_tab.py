import customtkinter as ctk

class LeaderboardTab:
    def __init__(self, parent):
        self.parent = parent
        
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self.parent, text="Leaderboard - Coming Soon!")
        self.label.grid(row=0, column=0, sticky="nsew")
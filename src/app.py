import customtkinter as ctk
from src.components.settings_tab import SettingsTab
from src.components.blind_comparison_tab import BlindComparisonTab
from src.components.leaderboard_tab import LeaderboardTab
from CTkMessagebox import CTkMessagebox
import tomllib  # Using tomllib for reading TOML files
import os
from appdirs import user_config_dir

class OllamaRankApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OllamaRank")
        self.geometry("1000x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Load settings
        self.settings = self.load_settings()

        # Create notebook (tabbed interface)
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create tabs
        self.settings_tab = self.notebook.add("Settings")
        self.blind_comparison_tab = self.notebook.add("Blind Side-by-Side")
        self.leaderboard_tab = self.notebook.add("Leaderboard")

        # Populate tabs
        self.settings_component = SettingsTab(self.settings_tab, self.enable_tabs, self.settings)
        self.blind_comparison = BlindComparisonTab(self.blind_comparison_tab, self.settings)
        self.leaderboard = LeaderboardTab(self.leaderboard_tab)

        # Initially set the correct tab states
        self.notebook.set("Settings")
        if self.settings and len(self.settings.get('models', [])) >= 5:
            self.enable_tabs()
        else:
            self.notebook._segmented_button.configure(state=["!disabled", "disabled", "disabled"])

    def load_settings(self):
        config_dir = user_config_dir("OllamaRank")
        config_path = os.path.join(config_dir, "settings.toml")
        if os.path.exists(config_path):
            with open(config_path, "rb") as f:
                return tomllib.load(f)  # Using tomllib.load to read the TOML file
        return None

    def enable_tabs(self):
        """Enable all tabs after settings are saved."""
        self.notebook._segmented_button.configure(state=["!disabled", "!disabled", "!disabled"])

def main():
    app = OllamaRankApp()
    app.mainloop()

if __name__ == "__main__":
    main()

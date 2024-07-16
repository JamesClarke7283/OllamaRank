import customtkinter as ctk
from src.components.settings_tab import SettingsTab
from src.components.blind_comparison_tab import BlindComparisonTab
from src.components.leaderboard_tab import LeaderboardTab
from src.core.database import db_manager
from src.core.ollama_service import OllamaService
from src.core.vote_outcome import VoteOutcome
from CTkMessagebox import CTkMessagebox
import tomllib
import os
from appdirs import user_config_dir
import asyncio
import threading

class OllamaRankApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OllamaRank")
        self.geometry("1000x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize database
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(db_manager.init_db())

        # Start the event loop in a separate thread
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()

        # Load settings
        self.settings = self.load_settings()

        # Initialize OllamaService
        self.ollama_service = OllamaService(self.settings.get('ollama_host', 'http://localhost'), 
                                            self.settings.get('ollama_port', '11434'))

        # Create notebook (tabbed interface)
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create tabs
        self.settings_tab = self.notebook.add("Settings")
        self.blind_comparison_tab = self.notebook.add("Blind Side-by-Side")
        self.leaderboard_tab = self.notebook.add("Leaderboard")

        # Populate tabs
        self.settings_component = SettingsTab(self.settings_tab, self.enable_tabs, self.settings)
        self.blind_comparison = BlindComparisonTab(self.blind_comparison_tab, self.settings, 
                                                   self.ollama_service, self.submit_vote)
        self.leaderboard = LeaderboardTab(self.leaderboard_tab, self.ollama_service)

        # Initially set the correct tab states
        self.notebook.set("Settings")
        if self.settings and len(self.settings.get('models', [])) >= 5:
            self.enable_tabs()
        else:
            self.notebook._segmented_button.configure(state=["!disabled", "disabled", "disabled"])

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def load_settings(self):
        config_dir = user_config_dir("OllamaRank")
        config_path = os.path.join(config_dir, "settings.toml")
        if os.path.exists(config_path):
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        return None

    def enable_tabs(self):
        """Enable all tabs after settings are saved."""
        self.notebook._segmented_button.configure(state=["!disabled", "!disabled", "!disabled"])

    def submit_vote(self, model_a_name, model_b_name, outcome: VoteOutcome):
        future = asyncio.run_coroutine_threadsafe(self._submit_vote(model_a_name, model_b_name, outcome), self.loop)
        try:
            future.result()  # Wait for the coroutine to complete
        except Exception as e:
            print(f"Error submitting vote: {str(e)}")
            self.after(0, lambda: CTkMessagebox(title="Error", message=f"Failed to submit vote: {str(e)}"))

    async def _submit_vote(self, model_a_name, model_b_name, outcome: VoteOutcome):
        try:
            model_a_info = await self.ollama_service.get_model_info(model_a_name)
            model_b_info = await self.ollama_service.get_model_info(model_b_name)

            model_a_modelfile = model_a_info.get('modelfile', '')
            model_b_modelfile = model_b_info.get('modelfile', '')

            await db_manager.record_vote(
                model_a_name, model_b_name, 
                model_a_modelfile, model_b_modelfile,
                outcome
            )

            # Refresh the leaderboard after submitting a vote
            self.after(0, self.leaderboard.refresh_leaderboard)
        except Exception as exc:
            print(f"Error in _submit_vote: {str(exc)}")
            raise exc  # Re-raise the exception to be caught by the submit_vote method
        
    def on_closing(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop_thread.join()
        self.loop.run_until_complete(db_manager.close_db())
        self.destroy()

def main():
    app = OllamaRankApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()

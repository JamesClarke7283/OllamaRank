import customtkinter as ctk
from src.core.database import db_manager
import asyncio
from src.core.ollama_service import OllamaService

class LeaderboardTab:
    def __init__(self, parent, ollama_service: OllamaService):
        self.parent = parent
        self.ollama_service = ollama_service
        
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        
        self.table_frame = ctk.CTkScrollableFrame(self.parent)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.headers = ["Rank", "Model", "Elo Rating", "Wins", "Losses", "Ties", "Bad", "Total Votes", ""]
        for i, header in enumerate(self.headers):
            label = ctk.CTkLabel(self.table_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        self.refresh_button = ctk.CTkButton(self.parent, text="Refresh Leaderboard", command=self.refresh_leaderboard)
        self.refresh_button.grid(row=1, column=0, pady=10)

    def refresh_leaderboard(self):
        # Clear existing data
        for widget in self.table_frame.winfo_children()[len(self.headers):]:
            widget.destroy()

        # Fetch and display new data
        try:
            asyncio.get_event_loop().run_until_complete(self.fetch_and_display_data())
        except Exception as e:
            print(f"Error refreshing leaderboard: {str(e)}")
            error_label = ctk.CTkLabel(self.table_frame, text=f"Error fetching leaderboard data: {str(e)}")
            error_label.grid(row=1, column=0, columnspan=len(self.headers), padx=5, pady=2, sticky="w")

    async def fetch_and_display_data(self):
        leaderboard_data = await db_manager.get_leaderboard()
        for rank, entry in enumerate(leaderboard_data, start=1):
            model = entry['model']
            row_data = [
                rank,
                model.name,
                f"{entry['elo_rating']:.2f}",
                entry['wins'],
                entry['losses'],
                entry['ties'],
                entry['both_bad'],
                entry['total_votes'],
            ]
            for j, item in enumerate(row_data):
                label = ctk.CTkLabel(self.table_frame, text=str(item))
                label.grid(row=rank, column=j, padx=5, pady=2, sticky="w")
            
            show_modelfile_button = ctk.CTkButton(
                self.table_frame, 
                text="Show Modelfile", 
                command=lambda m=model.name: self.show_modelfile(m),
                width=100
            )
            show_modelfile_button.grid(row=rank, column=len(row_data), padx=5, pady=2)

    async def show_modelfile(self, model_name):
        try:
            model_info = await self.ollama_service.get_model_info(model_name)
            modelfile = model_info.get('modelfile', 'Modelfile not available')
            
            # Create a new window to display the modelfile
            modelfile_window = ctk.CTkToplevel(self.parent)
            modelfile_window.title(f"Modelfile for {model_name}")
            modelfile_window.geometry("600x400")
            
            modelfile_text = ctk.CTkTextbox(modelfile_window, wrap="word")
            modelfile_text.pack(expand=True, fill="both", padx=10, pady=10)
            modelfile_text.insert("1.0", modelfile)
            modelfile_text.configure(state="disabled")
        except Exception as e:
            print(f"Error fetching modelfile for {model_name}: {str(e)}")
            error_window = ctk.CTkToplevel(self.parent)
            error_window.title("Error")
            error_window.geometry("300x100")
            error_label = ctk.CTkLabel(error_window, text=f"Error fetching modelfile: {str(e)}")
            error_label.pack(expand=True, fill="both", padx=10, pady=10)

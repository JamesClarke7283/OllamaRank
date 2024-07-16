import customtkinter as ctk
import random
import asyncio
from typing import List, Dict, Callable
from threading import Thread
from src.core.ollama_service import OllamaService
from src.core.vote_outcome import VoteOutcome

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, message="", is_user=False, **kwargs):
        super().__init__(master, fg_color=("gray75", "gray25") if is_user else ("gray85", "gray20"), corner_radius=20, **kwargs)
        self.message = ctk.CTkLabel(self, text=message, wraplength=350, justify="left")
        self.message.pack(padx=10, pady=5)

    def update_text(self, new_text):
        self.message.configure(text=new_text)

class BlindComparisonTab:
    def __init__(self, parent, settings: Dict, ollama_service: OllamaService, submit_vote_callback: Callable):
        self.parent = parent
        self.settings = settings
        self.models = settings.get('models', [])
        self.current_models = ["", ""]
        self.chat_bubbles = {"A": None, "B": None}
        self.responses_complete = {"A": False, "B": False}
        self.voting_enabled = False
        self.ollama_service = ollama_service
        self.submit_vote_callback = submit_vote_callback
        self.chat_history: Dict[str, List[Dict[str, str]]] = {}
        self.session_history: Dict[str, List[Dict[str, str]]] = {}

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        # Create chat frames
        self.chat_frame_a = ctk.CTkScrollableFrame(self.parent, label_text="Model A")
        self.chat_frame_a.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.chat_frame_b = ctk.CTkScrollableFrame(self.parent, label_text="Model B")
        self.chat_frame_b.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        # Create input field and send button
        self.input_frame = ctk.CTkFrame(self.parent)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_field = ctk.CTkEntry(self.input_frame, placeholder_text="Enter your message...")
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.input_field.bind("<Return>", lambda event: self.send_message())
        self.send_button.grid(row=0, column=1)

        # Create voting buttons (initially hidden)
        self.vote_frame = ctk.CTkFrame(self.parent)
        self.vote_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.vote_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.vote_a_button = ctk.CTkButton(self.vote_frame, text="A is better", command=lambda: self.vote("A"))
        self.vote_b_button = ctk.CTkButton(self.vote_frame, text="B is better", command=lambda: self.vote("B"))
        self.vote_tie_button = ctk.CTkButton(self.vote_frame, text="Tie", command=lambda: self.vote("Tie"))
        self.vote_bad_button = ctk.CTkButton(self.vote_frame, text="Both are bad", command=lambda: self.vote("Bad"))
        
        # Create New Round button (initially hidden)
        self.new_round_button = ctk.CTkButton(self.parent, text="New Round", command=self.new_comparison)
        self.new_round_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.new_round_button.grid_remove()

        self.hide_voting_buttons()
        self.new_comparison()

    def new_comparison(self):
        self.current_models = random.sample(self.models, 2)
        for widget in self.chat_frame_a.winfo_children():
            widget.destroy()
        for widget in self.chat_frame_b.winfo_children():
            widget.destroy()
        self.chat_frame_a.configure(label_text="Model A")
        self.chat_frame_b.configure(label_text="Model B")
        self.chat_bubbles = {"A": None, "B": None}
        self.responses_complete = {"A": False, "B": False}
        self.voting_enabled = False
        
        # Initialize chat history for new models
        self.chat_history = {
            "A": self.session_history.get(self.current_models[0], []),
            "B": self.session_history.get(self.current_models[1], [])
        }
        
        # Display previous messages
        for model in ["A", "B"]:
            for message in self.chat_history[model]:
                self.display_message(
                    self.chat_frame_a if model == "A" else self.chat_frame_b,
                    message['content'],
                    is_user=(message['role'] == 'user')
                )
        
        self.hide_voting_buttons()
        self.new_round_button.grid_remove()
        self.send_button.configure(state="normal")
        self.input_field.configure(state="normal")

    def send_message(self):
        user_message = self.input_field.get()
        if user_message:
            self.display_message(self.chat_frame_a, user_message, is_user=True)
            self.display_message(self.chat_frame_b, user_message, is_user=True)
            self.input_field.delete(0, "end")

            for model in ["A", "B"]:
                self.chat_history[model].append({"role": "user", "content": user_message})

            # Disable the input field and send button while waiting for responses
            self.input_field.configure(state="disabled")
            self.send_button.configure(state="disabled")

            # Run the async tasks in a new thread to not block the Tkinter main loop
            Thread(target=self.run_async_tasks, args=(user_message,), daemon=True).start()

    def run_async_tasks(self, user_message):
        asyncio.run(self.fetch_responses(user_message))

    async def fetch_responses(self, user_message):
        await asyncio.gather(
            self.get_model_response("A", self.current_models[0]),
            self.get_model_response("B", self.current_models[1])
        )

    async def get_model_response(self, model_letter, model_name):
        self.parent.after(0, lambda: self.create_response_bubble(model_letter))
        try:
            async for response in self.ollama_service.get_model_response(model_name, self.chat_history[model_letter]):
                self.parent.after(0, lambda r=response: self.update_chat_bubble(model_letter, r))
                await asyncio.sleep(0.01)  # Small delay to allow GUI updates
            self.chat_history[model_letter].append({"role": "assistant", "content": response})
            self.session_history[model_name] = self.chat_history[model_letter]
        except Exception as e:
            error_message = f"Error getting response from model: {str(e)}"
            self.parent.after(0, lambda: self.update_chat_bubble(model_letter, error_message))
        finally:
            self.parent.after(0, lambda: self.complete_response(model_letter))

    def create_response_bubble(self, model_letter):
        chat_frame = self.chat_frame_a if model_letter == "A" else self.chat_frame_b
        self.chat_bubbles[model_letter] = self.display_message(chat_frame, "")

    def display_message(self, chat_frame, message, is_user=False):
        bubble = ChatBubble(chat_frame, message, is_user)
        bubble.pack(padx=5, pady=5, anchor="e" if is_user else "w", fill="x")
        chat_frame._parent_canvas.yview_moveto(1.0)
        return bubble

    def update_chat_bubble(self, model, text):
        if self.chat_bubbles[model]:
            self.chat_bubbles[model].update_text(text)
            self.parent.update_idletasks()  # Force GUI update

    def complete_response(self, model):
        self.responses_complete[model] = True
        if all(self.responses_complete.values()):
            self.show_voting_buttons()
            self.voting_enabled = True
            # Enable the input field and send button after both responses are complete
            self.input_field.configure(state="normal")
            self.send_button.configure(state="normal")

    def show_voting_buttons(self):
        self.vote_a_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.vote_b_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.vote_tie_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.vote_bad_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def hide_voting_buttons(self):
        self.vote_a_button.grid_remove()
        self.vote_b_button.grid_remove()
        self.vote_tie_button.grid_remove()
        self.vote_bad_button.grid_remove()

    def vote(self, choice):
        if not self.voting_enabled:
            return

        model_a, model_b = self.current_models
        outcome = None

        if choice == "A":
            outcome = VoteOutcome.WIN
        elif choice == "B":
            outcome = VoteOutcome.LOSS
        elif choice == "Tie":
            outcome = VoteOutcome.TIE
        elif choice == "Bad":
            outcome = VoteOutcome.BOTH_BAD

        # Submit the vote asynchronously
        Thread(target=self.submit_vote_callback, args=(model_a, model_b, outcome), daemon=True).start()

        # Reveal the model names after voting
        self.chat_frame_a.configure(label_text=f"Model A: {model_a}")
        self.chat_frame_b.configure(label_text=f"Model B: {model_b}")
        
        # Disable input and show New Round button
        self.send_button.configure(state="disabled")
        self.input_field.configure(state="disabled")
        self.hide_voting_buttons()
        self.new_round_button.grid()

    def start_new_round(self):
        self.new_comparison()

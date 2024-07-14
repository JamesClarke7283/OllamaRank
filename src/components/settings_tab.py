import customtkinter as ctk
from typing import List, Callable, Dict
import tomli_w
import os
from appdirs import user_config_dir
import ollama
from CTkMessagebox import CTkMessagebox

class CustomListbox(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.items = []

    def insert(self, item):
        button = ctk.CTkButton(self, text=item, anchor="w", command=lambda: self.select(item))
        button.grid(row=len(self.items), column=0, sticky="ew", padx=5, pady=2)
        self.items.append((item, button))

    def delete(self, item):
        for i, (text, button) in enumerate(self.items):
            if text == item:
                button.destroy()
                self.items.pop(i)
                break
        self.repack()

    def repack(self):
        for i, (_, button) in enumerate(self.items):
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=2)

    def get(self):
        return [item for item, _ in self.items]

    def select(self, item):
        for text, button in self.items:
            if text == item:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray65", "gray30"))

    def get_selected(self):
        for text, button in self.items:
            if button.cget("fg_color") == ("gray75", "gray25"):
                return text
        return None

class SettingsTab:
    def __init__(self, parent, enable_tabs_callback: Callable, settings: Dict = None):
        self.parent = parent
        self.enable_tabs_callback = enable_tabs_callback
        self.available_models: List[str] = []
        self.selected_models: List[str] = []
        self.ollama_client = ollama.Client()

        self.parent.grid_columnconfigure((0, 1, 2), weight=1)
        self.parent.grid_rowconfigure(5, weight=1)

        # Ollama Host and Port
        self.host_label = ctk.CTkLabel(self.parent, text="Ollama Host:")
        self.host_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 0), sticky="w")
        self.host_entry = ctk.CTkEntry(self.parent)
        self.host_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.port_label = ctk.CTkLabel(self.parent, text="Ollama Port:")
        self.port_label.grid(row=2, column=0, columnspan=3, padx=10, pady=(10, 0), sticky="w")
        self.port_entry = ctk.CTkEntry(self.parent)
        self.port_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.refresh_button = ctk.CTkButton(self.parent, text="Refresh Models", command=self.fetch_models)
        self.refresh_button.grid(row=3, column=2, padx=10, pady=(0, 10), sticky="ew")

        # Model Selection
        self.available_label = ctk.CTkLabel(self.parent, text="Available Models:")
        self.available_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        self.selected_label = ctk.CTkLabel(self.parent, text="Selected Models:")
        self.selected_label.grid(row=4, column=2, padx=10, pady=(10, 0), sticky="w")

        self.available_listbox = CustomListbox(self.parent)
        self.available_listbox.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        
        self.selected_listbox = CustomListbox(self.parent)
        self.selected_listbox.grid(row=5, column=2, padx=10, pady=10, sticky="nsew")

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.parent)
        self.buttons_frame.grid(row=5, column=1, sticky="ns")
        self.buttons_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.move_right_button = ctk.CTkButton(self.buttons_frame, text="→", command=self.move_right, width=40)
        self.move_right_button.grid(row=0, column=0, pady=5)

        self.move_left_button = ctk.CTkButton(self.buttons_frame, text="←", command=self.move_left, width=40)
        self.move_left_button.grid(row=1, column=0, pady=5)

        self.move_all_right_button = ctk.CTkButton(self.buttons_frame, text="⇒", command=self.move_all_right, width=40)
        self.move_all_right_button.grid(row=2, column=0, pady=5)

        self.move_all_left_button = ctk.CTkButton(self.buttons_frame, text="⇐", command=self.move_all_left, width=40)
        self.move_all_left_button.grid(row=3, column=0, pady=5)

        # Save Button
        self.save_button = ctk.CTkButton(self.parent, text="Save", command=self.save_settings)
        self.save_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Load settings if provided
        if settings:
            self.load_settings(settings)
        else:
            self.host_entry.insert(0, "http://localhost")
            self.port_entry.insert(0, "11434")
            self.fetch_models()

    def load_settings(self, settings):
        self.host_entry.insert(0, settings.get('ollama_host', 'http://localhost'))
        self.port_entry.insert(0, settings.get('ollama_port', '11434'))
        self.selected_models = settings.get('models', [])
        self.update_selected_listbox()
        self.fetch_models()

    def fetch_models(self):
        host = self.host_entry.get()
        port = self.port_entry.get()
        self.ollama_client = ollama.Client(host=f"{host}:{port}")
        try:
            models = self.ollama_client.list()
            self.available_models = [model['name'] for model in models['models']]
            self.update_available_listbox()
        except Exception as e:
            print(f"Error fetching models: {e}")
            self.available_models = ["Error fetching models"]
            self.update_available_listbox()
            CTkMessagebox(title="Error", message=f"Failed to fetch models: {str(e)}")

    def update_available_listbox(self):
        self.available_listbox = CustomListbox(self.parent)
        self.available_listbox.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        for model in self.available_models:
            self.available_listbox.insert(model)

    def update_selected_listbox(self):
        self.selected_listbox = CustomListbox(self.parent)
        self.selected_listbox.grid(row=5, column=2, padx=10, pady=10, sticky="nsew")
        for model in self.selected_models:
            self.selected_listbox.insert(model)

    def move_right(self):
        selected = self.available_listbox.get_selected()
        if selected and selected in self.available_models:
            self.available_models.remove(selected)
            self.selected_models.append(selected)
            self.update_available_listbox()
            self.update_selected_listbox()

    def move_left(self):
        selected = self.selected_listbox.get_selected()
        if selected and selected in self.selected_models:
            self.selected_models.remove(selected)
            self.available_models.append(selected)
            self.update_available_listbox()
            self.update_selected_listbox()

    def move_all_right(self):
        self.selected_models.extend(self.available_models)
        self.available_models.clear()
        self.update_available_listbox()
        self.update_selected_listbox()

    def move_all_left(self):
        self.available_models.extend(self.selected_models)
        self.selected_models.clear()
        self.update_available_listbox()
        self.update_selected_listbox()

    def save_settings(self):
        if len(self.selected_models) < 5:
            CTkMessagebox(title="Error", message="Please select at least 5 models.")
            return

        config = {
            "ollama_host": self.host_entry.get(),
            "ollama_port": self.port_entry.get(),
            "models": self.selected_models
        }
        config_dir = user_config_dir("OllamaRank")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "settings.toml")
        with open(config_path, "wb") as f:
            tomli_w.dump(config, f)
        print(f"Settings saved to {config_path}")
        self.enable_tabs_callback()
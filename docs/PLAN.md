# Plan For Ollama Rank

The app: Ollama Rank, aims to mimic the LMSYS chatbot arena, we use a CustomTkinter Notebook tab with three tabs.

1. Settings: To start, you need to put in the Ollama Host and port. Then, add the models using the dropdown to select and add new models to enter into the Arena, once you are ready, click "Save", the other two tabs will become available after that, all settings are stored in the config directory under OllamaRank, under a file called settings.toml which is where the settings will be saved.

2. "Blind Side-By-Side" mode, like the chatbot arena, we will pick 2 random chatbots to chat side-by-side, you can vote "Tie","Chatbot A","Chatbot B", "Both Bad", after you have voted the names of the chatbots you have used are revealed, results (including conversation details and outcome(how you voted)) are stored in a sqlite3 file, and use toroice-orm, use appdirs to determine the appropriate place in a folder called OllamaRank, but what folder in the home directory to put data about the application, it also needs to be able to have multiple messages in its history so it can remember and have a conversation.

3. Leaderboard: Contains the number-rank(what number place it is in), the model name, then the Elo Number, Number of votes. sorted in order of rank, and Modelfile (Show the modelfile of each model, by clicking).

File structure:
LICENSE.md
README.md
assets/
assets/LICENSE
assets/logo.webp
assets/screenshot.webp
docs/
docs/PLAN.md
pyproject.toml
src/
src/__init__.py
src/app.py
src/components/
src/components/blind_comparison_tab.py
src/components/custom_widgets.py
src/components/leaderboard_tab.py
src/components/settings_tab.py
src/core/
src/core/models/

*Note*: models does not mean LLMs, its a folder that stores the TortoiceORM models for the data.
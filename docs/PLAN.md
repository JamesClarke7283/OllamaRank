# Plan For Ollama Rank

The app: Ollama Rank, aims to mimic the LMSYS chatbot arena, we use a CustomTkinter Notebook tab with three tabs.

1. Settings: To start, you need to put in the Ollama Host and port. Then, add the models using the dropdown to select and add new models to enter into the Arena, once you are ready, click "Save", the other two tabs will become available after that, all settings are stored in the config directory under OllamaRank, under a file called settings.toml which is where the settings will be saved.

2. "Blind Side-By-Side" mode, like the chatbot arena, we will pick 2 random chatbots to chat side-by-side, you can vote "Tie","Chatbot A","Chatbot B", "Both Bad", after you have voted the names of the chatbots you have used are revealed, results (including conversation details and outcome(how you voted)) are stored in a sqlite3 file, and use toroice-orm, use appdirs to determine the appropriate place in a folder called OllamaRank, but what folder in the home directory to put data about the application, it also needs to be able to have multiple messages in its history so it can remember and have a conversation.

3. Leaderboard: Contains the number-rank(what number place it is in), the model name, then the Elo Number. sorted in order of rank.



File structure:
.
├── docs
│   └── PLAN.md
├── LICENSE.md
├── pyproject.toml
├── README.md
└── src
    ├── app.py
    ├── components
    └── core
        └── models

*Note*: models does not mean LLMs, its a folder that stores the TortoiceORM models for the data.

pyproject.toml:
[build-system]
requires = ["setuptools>=45", "setuptools_scm[toml]>=6.2", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "OllamaRank"
dynamic = ["version"]
description = "A LLM evaluator similar to LMSYS chatbot arena, using the Elo ranking system"
authors = [
    {name = "James David Clarke", email = "james@jamesdavidclarke.com"},
]
license = {text = "GPL-3.0-or-later"}
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    "customtkinter",
    "ollama",
    "tomli-w",
    "appdirs",
    "tortoise-orm"
]

[project.optional-dependencies]
dev = [
    "black",
    "isort",
    "mypy",
]

[project.urls]
Homepage = "https://github.com/JamesClarke7283/OllamaRank"
"Bug Tracker" = "https://github.com/JamesClarke7283/OllamaRank/issues"

[tool.setuptools.packages.find]
where = ["src"]
include = ["ollamarank*"]

[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
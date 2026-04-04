# Python AI Experimentation  🐍

This project will use [Ruff](https://docs.astral.sh/ruff/) for linting and [Visual Studio Code](https://code.visualstudio.com/) for development.

## 📁 Project Structure
006 - AI_COLLABORATION/
├── .vscode/              # VS Code workspace settings
│   └── settings.json
├── src/                  # Source code lives here
    └── app_controller.py
    └── cli.py
    └── config_manager.py
    └── context_loader.py
    └── context_manager.py
    └── conversation_manager.py
    └── conversation.py
    └── dispatcher.py
    └── file_generator.py
    └── main.py
    └── model_runner.py
    └── thinking_display.py
    └── utils.py
├── command_contract.txt
├── conversation_contract.txt
├── pyproject.toml        # Ruff configuration information
├── .gitignore
└── README.md             # Project overview






                          ┌──────────────────────┐
                          │     AppController    │
                          │ (orchestrates flow)  │
                          └──────────┬───────────┘
                                     │
     ┌───────────────────────────────┼───────────────────────────────┐
     │                               │                               │
     ▼                               ▼                               ▼
┌──────────────────┐             ┌───────────────────┐            ┌────────────────┐
│ContextManager    │             │ConversationManager│            │  ModelRunner   │
│(builds initial   │             │ (manages state)   │            │ (executes model│
│initial context   │             │                   │            │    calls)      │
│and conversation) │             └────────────────┬──┘            └────────────────┘
└──────┬───────────┘                              │
       │                                          │
       ▼                                          ▼
┌────────────────┐                     ┌───────────────┐
│  Conversation  │ <------------------ │   Dispatcher  │
│  (data object) │   (commands modify  │  (/commands)  │
└────────────────┘     conversation)   └───────────────┘


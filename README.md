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



📐 High‑Level Architecture Diagram

                          ┌──────────────────────┐
                          │     AppController    │
                          │  (orchestrates flow) │
                          └──────────┬───────────┘
                                     │
        ┌────────────────────────────┼─────────────────────────────┐
        │                            │                             │
        ▼                            ▼                             ▼
┌───────────────────┐        ┌────────────────────┐         ┌──────────────────┐
│  ContextManager   │        │ ConversationManager│         │   ModelRunner    │
│ (builds initial   │        │  (manages convo    │         │ (executes model  │
│  context + convo) │        │   state/mutations) │         │      calls)      │
└─────────┬─────────┘        └──────────┬─────────┘         └─────────┬────────┘
          │                             │                            │
          │                             │                            │
          ▼                             ▼                            ▼
   ┌───────────────┐           ┌───────────────┐            ┌────────────────┐
   │  Conversation │ <-------- │   Dispatcher  │            │  ModelManager  │
   │ (data object) │  (commands│  (/,- commands│            │ (model metadata│
   └───────────────┘   mutate) │   → handlers) │            │  & queries)    │
                               └───────────────┘            └────────────────┘
Additional components:
    ┌──────────────────┐          ┌──────────────────┐
    │  FileGenerator   │          │  ThinkingDisplay │
    │ (exports, files) │          │ (GUI/CLI stream  │
    └──────────────────┘          │  visualization)  │
                                  └──────────────────┘
    ┌──────────────────┐
    │  ContextLoader   │
    │ (files/dirs →    │
    │  context chunks) │
    └──────────────────┘

# AppController
Role: Orchestrator and lifecycle owner.
Owns:
- app_start, app_run, app_repl
- create_conversation, start_new_conversation, switch_conversation
- run_initial_conversation_turn
- conversations dict, active_conversation_id, active_conversation (read‑only)

Calls into:
- ContextManager (build conversation)
- ConversationManager (mutate messages)
- ModelRunner (LLM calls)
-Dispatcher (slash/dash commands)
- ModelManager (model info, if needed)

Does not:
- parse commands itself
- know about file formats
- own model metadata

# --- 
# Conversation, ContextManager, and ConversationManager
This cluster defines the core data model and the two managers responsible for
creating and mutating conversation state. These three components work together
but have strictly separated responsibilities.
# ---

## Conversation (data object)
Role: Pure data container - holds all state relevant to a single conversation but contains no business logic.
Intentionally simple and dependency-free

Fields typically include:
- persona
- model_name
- messages (list of message dicts or objects)
- options (temperature, max tokens, etc.)
- context_attachments (optional list of context chunks)

The Conversation object must not import or depend on:
- AppController
- Dispatcher
- Any manager class

## ContextManager
Role: Responsible for constructing new Conversation objects and initializing them with persona‑specific system messages/context.

Responsibilities:
- Maintain persona definitions and metadata
- start_conversation(persona_name):
    - create a new Conversation object
    - seed system messages
    - attach initial persona context
- Integrate context chunks into a conversation when requested

Not responsible for:
- Adding user or AI messages
- Running models
- Managing multiple conversations
- Parsing commands

Allowed dependencies:
- Conversation (data class)
- ContextLoader (optional, for file/directory ingestion)

## ConversationManager
Role: Responsible for mutating the state of an existing Conversation object - provides the only sanctioned way to modify messages/context after conversation creation

Responsibilities:
- add_user_message(conversation, text)
- add_ai_response(conversation, response)
- clear_history(conversation)
- truncate_history(conversation, strategy)
- attach_context(conversation, context_chunks)

Not responsible for:
- Creating conversations (ContextManager)
- Running models (ModelRunner)
- Orchestrating application flow (AppController)
- Parsing commands (Dispatcher)

Allowed dependencies:
- Conversation (data class)

# --- 
# ModelRunner and ModelManager
These components handle all model‑related operations. Their responsibilities are strictly separated: ModelRunner executes inference, while ModelManager
provides metadata and model availability information. Neither manages conversations or application flow.
# ---

## ModelRunner
Role: ModelRunner is responsible for executing model inference. It is the only component that communicates with the underlying LLM backend (e.g., Ollama).

Responsibilities:
- run_conversation(model, messages, options):
    - execute a model call using the provided messages and options
    - return a structured response object
- handle model execution errors
- provide a consistent interface for AppController and ConversationManager

Not responsible for:
- Tracking available or installed models
- Managing conversations
- Parsing commands
- Application lifecycle

Allowed dependencies:
- Model backend client or subprocess calls
- Standard library utilities

ModelRunner must not depend on:
- AppController
- Dispatcher
- ContextManager
- ConversationManager

## ModelManager
Role: Provides model metadata and availability information - does not run inference and does not interact with conversation state.

Responsibilities:
- get_downloaded_models():
    - wrap `ollama list` to return installed models
- get_running_models():
    - wrap `ollama ps` to return active model processes
- get_available_models():
    - fetch the Ollama library page and return raw or parsed results
- serve as the single source of truth for model metadata

Not responsible for:
- Running inference (ModelRunner)
- Application lifecycle (AppController)
- Parsing commands (Dispatcher)
- Managing conversation state

Allowed dependencies:
- Standard library (subprocess, urllib.request, etc.)

ModelManager must not depend on:
- AppController
- Dispatcher
- ConversationManager
- ModelRunner

# --- 
# Dispatcher and ContextLoader
These components handle command parsing and context ingestion. Dispatcher routes
user commands to handlers, while ContextLoader converts files and directories
into context chunks that can be attached to conversations.
# ---

## Dispatcher
Role: The command routing layer for slash (/) and dash (-) commands - parses user input, identifies the appropriate command handler, and executes it.
Dispatcher must remain stateless and must not depend on AppController.

Responsibilities:
- system_dispatch(cmd, conversation, ...):
    - parse slash commands
    - route to system-level handlers
- conversation_dispatch(cmd, conversation, ...):
    - parse dash commands
    - route to conversation-level handlers
- Build argument parsers using argparse and shlex
- Map command keywords to handler functions
- Execute handlers that operate on:
    - Conversation
    - ContextLoader
    - ModelManager
    - ConversationManager

Not responsible for:
- Managing application lifecycle
- Managing conversation registry
- Running model inference
- Creating or switching conversations

Allowed dependencies:
- ModelManager
- ContextLoader
- ConversationManager
- Standard library (argparse, shlex)

Dispatcher must not depend on:
- AppController
- ModelRunner
- ContextManager


## ContextLoader
Role: Responsible for converting external files and directories into context chunks that can be attached to a Conversation. It performs file I/O,
parsing, and chunking, but does not decide when or why context is loaded

Responsibilities:
- file_to_context(conversation, path):
    - read a file from disk
    - convert its contents into context chunks
    - attach chunks to the conversation
- directory_to_context(conversation, path):
    - iterate through directory contents
    - load each file into context
- Handle file I/O errors gracefully
- Provide reusable utilities for context ingestion

Not responsible for:
- Creating conversations
- Managing conversation state (beyond attaching context)
- Running models
- Parsing commands

Allowed dependencies:
- Standard library (os, pathlib, file I/O)
- Conversation (data object)

ContextLoader must not depend on:
- AppController
- Dispatcher
- ModelRunner
- ModelManager

# --- 
# FileGenerator
Role: Responsible for exporting artifacts derived from conversations or model output - does not participate in application flow, model execution, or command parsing.
# ---

Responsibilities:
- Export conversation logs to disk
- Generate files from model output (reports, summaries, transcripts, etc.)
- Provide reusable utilities for file creation and formatting

Not responsible for:
- Running models
- Managing conversation state
- Parsing commands
- Application lifecycle

Allowed dependencies:
- Standard library (file I/O, formatting utilities)

FileGenerator must not depend on:
- AppController
- Dispatcher
- ModelRunner
- ModelManager
- ConversationManager

# --- 
# ThinkingDisplay and Dependency Summary
Role: Handles visualization of intermediate or streaming output from the model. It is a presentation-layer component and does not affect application logic or conversation state.
# ---

Responsibilities:
- Render intermediate tokens or "thinking" output
- Integrate with CLI or GUI display mechanisms
- Provide hooks for streaming model responses

Not responsible for:
- Running models
- Managing conversations
- Parsing commands
- Application lifecycle

Allowed dependencies:
- Standard library (printing, formatting)
- Optional GUI libraries (if used in the future)

ThinkingDisplay must not depend on:
- AppController
- Dispatcher
- ModelRunner
- ModelManager
- ConversationManager

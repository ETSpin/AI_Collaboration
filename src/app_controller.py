"""
Class: AppController
Author: MORS
Date: 22 MAR 26

Description:
Coordinates the major subsystems (ModelRunner, ConversationManager, ContextManager,
FileGenerator, ThinkingDisplay) to keep main.py clean and maintainable. Provides a
central lifecycle for creating, switching, and running conversations.

 Responsibilities (Post-Refactor):
   - Maintain a registry of all Conversation objects created during runtime.
   - Track which conversation is currently active.
   - Create new conversations via create_conversation().
   - Assign unique conversation IDs via Utils.generate_conv_id().
   - Switch the active conversation via switch_conversation().
   - Run the initial model turn for a new conversation (persona introduction).
   - Provide a unified lifecycle entry point via start_new_conversation().
   - Manage the CLI REPL loop for user input and command dispatch.
   - Route slash commands to dispatcher.system_dispatch().
   - Route dash commands to dispatcher.conversation_dispatch().
   - Append user and AI messages via ConversationManager.
   - Integrate with GUI mode via update_chat_display() and update_thinking_display().
   - Support GUI-driven temperature/model option updates through the Conversation object.

 Not Responsible For:
   - Implementing model logic (delegated to ModelRunner).
   - Mutating Conversation internals directly (delegated to ConversationManager).
   - Rendering GUI elements or managing GUI state.
   - Managing filesystem context or file ingestion.
   - Exporting files, logs, or external artifacts.

 Public API Contract (Post-Refactor):

   Instance Methods:

     - __init__()
         Inputs: none
         Outputs: AppController instance
         Notes: initializes conversation registry, active ID, and GUI reference

     - conversations (property)
         Inputs: none
         Outputs: dict[str, Conversation]

     - active_conversation (property)
         Inputs: none
         Outputs: Conversation or None
         Notes: read-only convenience accessor

     - app_start(persona_name: str = "pymetheus")
         Inputs: persona_name
         Outputs: conversation_id
         Side Effects: calls start_new_conversation()

     - app_run()
         Inputs: none
         Outputs: none
         Side Effects: calls app_start() then app_repl()

     - app_repl()
         Inputs: none
         Outputs: none
         Side Effects: REPL loop, dispatches commands, runs model

     - create_conversation(persona_name)
         Inputs: persona_name
         Outputs: conversation_id
         Notes: pure creation; does NOT switch active conversation

     - switch_conversation(conv_id)
         Inputs: conv_id
         Outputs: bool (success)
         Notes: updates active_conversation_id

     - run_initial_conversation_turn(conv_id)
         Inputs: conv_id
         Outputs: model response or False
         Notes: rruns persona introduction turn and pushes output to GUI/CLI

     - start_new_conversation(persona_name)
         Inputs: persona_name
         Outputs: conversation_id or False
         Notes: full lifecycle: create → switch → initial turn

     - list_conversations()
         Inputs: none
         Outputs: list[str]

     - run_conversation_turn(user_input)
         Inputs: user_input
         Outputs: response.message.content [str]
         Notes: runs one turn of the conversation (user input - computer response)

     - update_chat_display(text, window_id=None)
         Inputs: text, window_id
         Outputs: none
         Notes: Groutes output to GUI if present, otherwise prints to CLI

     - update_thinking_display(output_chunk, window_id=None)
         Inputs: output_chunk, window_id
         Outputs: none
         Notes: GUI placeholder

   Static Methods:
     - None
"""

import json
import os

import dispatcher
from context_manager import ContextManager
from conversation_manager import ConversationManager
from utils import Utils


class AppController:
    # AppController object initator
    def __init__(self):
        self._conversations = {}
        self._active_conversation_id = None
        self.gui = None

        self.personas = self._load_personas()

        self.context_manager = ContextManager()

    @property
    def conversations(self):
        return self._conversations

    @property
    def active_conversation_id(self):
        return self._active_conversation_id

    @property
    def active_conversation(self):
        return self._conversations.get(self._active_conversation_id)

    # Initialize a new conversation with the selected persona
    def app_start(self, persona_name: str = "pymetheus"):
        conv_id = self.start_new_conversation(persona_name)
        return conv_id

    # Main loop for user interaction
    def app_repl(self):
        while True:
            user_input = input("User: ")
            if not user_input:
                break  # exit on blank input
            conv = self.active_conversation

            # Slash commands → system dispatcher
            if user_input.startswith("/"):
                dispatcher.system_dispatch(user_input[1:], conv)
                continue

            # Dash commands → conversation dispatcher
            if user_input.startswith("-"):
                dispatcher.conversation_dispatch(user_input[1:], conv)
                continue

            response_text = self.run_conversation_turn(user_input)
            self.update_chat_display(f"{response_text}\n")

    # Creates the conversation and assigns it to the conversations dict with an id
    def create_conversation(self, persona_name, user_overrides=None):  # user override will be fleshed out later
        print("[AppController] Creating conversation...")

        persona = self.context_manager.get_persona(self.personas, persona_name)
        if persona is None:
            print(f"[AppController] Persona '{persona_name}' not found.")
            return None

        context_components = self.context_manager.build_context_components(persona)
        model_name = persona["model"]
        persona_defaults = persona["defaults"]
        conversation = ConversationManager.start_conversation(
            persona_name=persona_name, persona_dict=persona, context_components=context_components, default_settings=persona_defaults, model_name=model_name
        )

        conv_id = Utils.generate_conv_id()
        conversation.conversation_id = conv_id

        self.conversations[conv_id] = conversation

        return conv_id

    # Entry point for the application
    def app_run(self):
        self.app_start()
        self.app_repl()

    # Switch the active conversation to the passed conv_id
    def switch_conversation(self, conv_id):
        if conv_id in self.conversations:
            self._active_conversation_id = conv_id
            return True

        print(f"No conversation with id: {conv_id}")
        return False

    # This handles one turn of the conversation
    def run_conversation_turn(self, user_input):
        conv = self.active_conversation

        ConversationManager.add_user_message(conv, user_input)
        response = ConversationManager.run_model(conv)
        ConversationManager.add_ai_response(conv, response)

        return response.message.content

    # Return basic information about "available" conversations
    def list_conversations(self):
        convo_list_info = []
        for convo_id, convo_obj in self.conversations.items():
            entry = {
                "id": convo_id,
                "model": convo_obj.model_name,
                "model_settings": convo_obj.model_settings,
                "title": getattr(convo_obj, "title", None),
                "created_at": getattr(convo_obj, "created_at", None),
                "updated_at": getattr(convo_obj, "updated_at", None),
            }
            convo_list_info.append(entry)

        return convo_list_info

    # First model response (persona introduction)
    def run_initial_conversation_turn(self, conv_id):
        if conv_id not in self.conversations:
            return False
        conversation = self.conversations[conv_id]
        response = ConversationManager.run_model(conversation)
        ConversationManager.add_ai_response(conversation, response)
        self.update_chat_display(f"{response.message.content}\n")
        self.gui.chat_display.insert("end", "──────────────────────────────\n\n")
        self.gui.chat_display.see("end")

    # Create and start a new conversation
    def start_new_conversation(self, persona_name):
        if self.context_manager.get_persona(self.personas, persona_name) is None:
            print(f"[AppController] Persona '{persona_name}' not found.")
            return None
        conversation_id = self.create_conversation(persona_name)
        if conversation_id is None:
            return None

        self.switch_conversation(conversation_id)
        self.run_initial_conversation_turn(conversation_id)

        return conversation_id

    def get_active_conversation_summary(self):
        conv = self.active_conversation
        if not conv:
            return None
        return {
            "id": self.active_conversation_id,
            "model": conv.model_name,
            "model_settings": conv.model_settings,
            "title": conv.title,
            "messages": conv.messages,
            "created_at": getattr(conv, "created_at", None),
            "updated_at": getattr(conv, "updated_at", None),
        }

    # Update the chat display with the response from the model - enables CLI or GUI
    def update_chat_display(self, text, window_id=None):
        if self.gui is not None:
            self.gui.chat_display.insert("end", text)
            self.gui.chat_display.see("end")
        else:
            # CLI mode
            print(text, end="")

    # Optional: update the GUI thinking indicator during streaming output
    def update_thinking_display(self, output_chunk, window_id=None):
        if self.gui is not None:
            # GUI mode: append partial output to a "thinking" widget if present
            if hasattr(self.gui, "thinking_display"):
                self.gui.thinking_display.insert("end", output_chunk)
                self.gui.thinking_display.see("end")
        else:
            # CLI mode: do nothing (streaming not required)
            pass

    # Persona loader from read personalities.json 
    def _load_personas(self):
        base_dir = os.path.dirname(__file__)
        personas_path = os.path.join(base_dir, "./personalities.json")

        if not os.path.exists(personas_path):
            print(f"[AppController] Persona file not found: {personas_path}")
            return {}

        with open(personas_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            print("[AppController] Invalid persona file format (expected dict).")
            return {}

        return data
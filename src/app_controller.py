"""
Class: AppController
Author: MORS
Date: 22 MAR 26

Description:
Coordinates the major subsystems (ModelRunner, ConversationManager, ContextManager,
FileGenerator, ThinkingDisplay) to keep main.py clean and maintainable. Provides a
central lifecycle for creating, switching, and running conversations.

 Responsibilities:
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
from runtime_monitor import RuntimeMonitor
from utils import Utils


class AppController:
    # AppController object initator
    def __init__(self):
        self._conversations = {}
        self._active_conversation_id = None
        self.gui = None

        self.personas = self._load_personas()

        self.context_manager = ContextManager()
        self.tokens_system_max = RuntimeMonitor.estimate_tokens_hardware_max()

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
                print("[AppController]: Dash Command fired")
                result = dispatcher.conversation_dispatch(user_input[1:], conv)
                if not result:
                    continue

                # DEBUG: inspect GUI state
                print("DEBUG: gui =", self.gui)
                if self.gui is not None:
                    print("DEBUG: gui.chat_display =", getattr(self.gui, "chat_display", None))

                if result.get("user_message"):
                    ConversationManager.notify_context_updated(conv, result["user_message"])
                    self.update_chat_display(result["user_message"] + "\n")
                if result.get("model_prompt"):
                    self.force_model_acknowledgement(result["model_prompt"])
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

    # Helper function to ensure the model acknowledges context changes.
    def force_model_acknowledgement(self, text):
        response_text = self.run_conversation_turn(text)
        self.update_chat_display(response_text + "\n")

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
        self.update_txt_chat_display(f"{response.message.content}\n")
        self.gui.txt_chat_display.insert("end", "──────────────────────────────\n\n")
        self.gui.txt_chat_display.see("end")

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
    def update_txt_chat_display(self, text, window_id=None):
        if self.gui is not None:
            self.gui.txt_chat_display.insert("end", text)
            self.gui.txt_chat_display.see("end")
        else:
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

    # Return the full conversation context text - formatted
    def get_active_conversation_context_text(self):
        conv = self.active_conversation
        if conv is None:
            return "No active conversation"

        context_dict = ConversationManager.get_full_context(conv)
        return self.format_context_for_display(context_dict, conv)

    # AI generated to help clean up the formatting for the Context Window -- what a mess
    def format_context_for_display(self, context_dict, conv):
        def section(title):
            return f"--- {title} ---"

        def fmt_dict(d, indent=4):
            lines = []
            pad = " " * indent
            for k, v in d.items():
                if isinstance(v, dict):
                    lines.append(f"{k}:")
                    for sk, sv in v.items():
                        lines.append(f"{pad}{sk}: {sv}")
                else:
                    lines.append(f"{k}: {v}")
            return "\n".join(lines)

        out = []

        # ============================================================
        # HEADER
        # ============================================================
        out.append("=== MODEL CONTEXT ===")
        out.append(f"Conversation ID: {conv.conversation_id}")
        out.append(f"Persona: {conv.persona_name}")
        out.append(f"Model: {conv.model_name}")
        out.append("")

        # ============================================================
        # MODEL SETTINGS
        # ============================================================
        out.append(section("Model Settings"))
        out.append(fmt_dict(conv.model_settings))
        out.append("")

        # ============================================================
        # PERSONA
        # ============================================================
        persona = context_dict.get("persona_components", {})
        persona_dict = persona.get("persona_dict", {})

        out.append(section("Persona"))
        out.append(f"Name: {persona_dict.get('name', '')}")
        out.append(f"Model: {persona_dict.get('model', '')}")
        out.append("")

        if persona_dict.get("description"):
            out.append("Description:")
            out.append(persona_dict["description"])
            out.append("")

        if persona_dict.get("personality"):
            out.append("Personality:")
            out.append(persona_dict["personality"])
            out.append("")

        if persona_dict.get("defaults"):
            out.append("Defaults:")
            out.append(fmt_dict(persona_dict["defaults"], indent=6))
            out.append("")

        # ============================================================
        # CONTEXT COMPONENTS
        # ============================================================
        out.append(section("Context Components"))
        out.append(fmt_dict(context_dict.get("context_components", {})))
        out.append("")

        # ============================================================
        # DIRECTORY SUMMARY
        # ============================================================
        out.append(section("Directory Summary"))
        summary = context_dict.get("directory_summary", "")
        out.append(summary if summary else "(No directory loaded)")
        out.append("")

        # ============================================================
        # LOADED FILES (filenames only)
        # ============================================================
        out.append(section("Loaded Files"))
        files = context_dict.get("files", [])
        if files:
            for f in files:
                out.append(f)
        else:
            out.append("(No files loaded)")
        out.append("")

        # ============================================================
        # EMBEDDINGS
        # ============================================================
        out.append(section("Embeddings"))

        # out.append(f"Status: {conv.embed_status}")
        # out.append(f"Backend: {conv.embed_backend}")
        out.append(f"Index Path: {conv.embed_index_path}")
        out.append(f"Location: {conv.embed_location}")
        out.append(f"Last Built: {conv.embed_last_built_at}")
        # out.append(f"Chunk Size: {conv.embed_chunk_size}")
        # out.append(f"Chunk Overlap: {conv.embed_chunk_overlap}")

        if conv.embed_files:
            out.append("Files Embedded:")
            for f in conv.embed_files:
                out.append(f"  {f}")
        else:
            out.append("Files Embedded: (none)")

        if conv.embed_stats:
            out.append("Stats:")
            out.append(fmt_dict(conv.embed_stats, indent=6))
        else:
            out.append("Stats: (none)")

        out.append("")

        # ============================================================
        # SYSTEM MESSAGES ONLY
        # ============================================================
        out.append(section("System Messages"))
        messages = context_dict.get("messages", [])
        system_msgs = [m for m in messages if m.get("role") == "system"]

        if system_msgs:
            for m in system_msgs:
                out.append(m.get("content", "").strip() + "\n")
        else:
            out.append("(No system messages)\n")

        return "\n".join(out)

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


import dispatcher
from context_manager import ContextManager
from conversation import Conversation
from conversation_manager import ConversationManager
from model_runner import ModelRunner
from utils import Utils


class AppController:
    
    # AppController object initator 
    def __init__(self):
        self._conversations = {}
        self._active_conversation_id = None
        self.gui = None

        self.context_manager = ContextManager()
        self.context_manager.load_personas()

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

            # Slash and Dash commands
            if user_input.startswith("/"):
                dispatcher.system_dispatch(user_input[1:], conv)
                continue

            if user_input.startswith("-"):
                dispatcher.conversation_dispatch(user_input[1:], conv)
                continue
            
            conversation_turn = self.run_conversation_turn(user_input)
            print(f"{conv.persona.capitalize()}:", conversation_turn)


    # Creates the conversation and assigns it to the conversations dict with an id
    def create_conversation(self, persona_name, user_overrides=None): #user override will be fleshed out later
        print("[AppController] Creating conversation...")

        persona = self.context_manager.get_persona(persona_name)
        if persona is None:
            print(f"[AppController] Persona '{persona_name}' not found.")
            return None
        persona_defaults = persona["defaults"]
        model_name = persona["model"]
        model_options = {"num_ctx": persona_defaults.get("num_ctx"), "temperature": persona_defaults.get("temperature"), "top_p": persona_defaults.get("top_p"), "top_k": persona_defaults.get("top_k"), "repeat_penalty": persona_defaults.get("repeat_penalty"),}
        model_options = {k: v for k, v in model_options.items() if v not in ("", None)} #remove blanks

        start_messages = [{"role": "system", "content": persona.get("personality") or ""},{"role": "user", "content": "Hello."}]

        """ This will come later
        Merge defaults with user overrides
        merged_options = copy of persona_defaults
        if user_overrides is not None:
        merged_options.update(user_overrides) 
        """
        conversation = Conversation(model_name=model_name,messages=start_messages,model_options=model_options)
        #conversation = self.context_manager.start_conversation(persona_name=persona_name,model_name=model_name,options=persona_defaults) 
        
        conversation._persona = persona_name
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
        response = ModelRunner.run_conversation(model=conv.model_name,messages=conv.messages, options=conv.options)
        ConversationManager.add_ai_response(conv, response)
        
        return response.message.content
    
    # Return basic information about "available" conversations
    def list_conversations(self):
        convo_list_info = []
        for convo_id, convo_obj in self.conversations.items():
            entry = {"id": convo_id, "persona": convo_obj.persona,"model": convo_obj.model_name, "title": getattr(convo_obj, "title", None), "created_at": getattr(convo_obj, "created_at", None),
                "updated_at": getattr(convo_obj, "updated_at", None),}
            convo_list_info.append(entry)
    
        return convo_list_info
    
    # First model response (persona introduction)
    def run_initial_conversation_turn(self, conv_id):
        if conv_id not in self.conversations:
            return False
        conversation = self.conversations[conv_id]
        response = ModelRunner.run_conversation(model=conversation.model_name, messages=conversation.messages, options=conversation.options)
        ConversationManager.add_ai_response(conversation, response)
        self.update_chat_display(f"{conversation.persona.capitalize()}: {response.message.content}\n"
)

    # Create and start a new conversation
    def start_new_conversation(self, persona_name):
        if self.context_manager.get_persona(persona_name) is None:
            print(f"[AppController] Persona '{persona_name}' not found.")
            return None
        conversation_id = self.create_conversation(persona_name)
        self.switch_conversation(conversation_id)
        self.run_initial_conversation_turn(conversation_id)
        return conversation_id

    def get_active_conversation_summary(self):
        conv = self.active_conversation
        if not conv:
            return None
        return {
            "id": self.active_conversation_id,
            "persona": conv.persona,
            "title": conv.title,
            "messages": conv.messages,
        }

    # Update the chat display with the response from the model - enables CLI or GUI 
    def update_chat_display(self, text, window_id=None):
        if self.gui is not None:
            self.gui.chat_display.insert("end", text)
            self.gui.chat_display.see("end")
        else:
            print(text)
    
    # Update the thinking display during streaming output
    def update_thinking_display(self, output_chunk, window_id=None):
        pass
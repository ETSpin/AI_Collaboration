"""
Class: AppController
Author: MORS
Date: 22 MAR 26

Description:
Coordinates the major subsystems (ModelRunner, ConversationManager, ContextManager,
FileGenerator, ThinkingDisplay) to keep main.py clean and maintainable. Provides a
central lifecycle for creating, switching, and running conversations.

 Responsibilities (Post‑Refactor):
   - Maintain a registry of all Conversation objects created during runtime.
   - Track which conversation is currently active.
   - Create new conversations via create_conversation().
   - Generate unique conversation IDs via Utils.generate_conv_id().
   - Switch the active conversation via switch_conversation().
   - Run the initial model turn for a new conversation.
   - Provide a unified lifecycle entry point via start_new_conversation().
   - Manage the REPL loop for user input and command dispatch.
   - Route slash commands to dispatcher.system_dispatch().
   - Route dash commands to dispatcher.conversation_dispatch().
   - Append user and AI messages via ConversationManager.
   - Provide placeholder hooks for GUI updates (chat + thinking displays).
   - Provide a placeholder for context integration.

 Not Responsible For:
   - Implementing model logic (delegated to ModelRunner).
   - Mutating Conversation internals directly (delegated to ConversationManager).
   - Rendering GUI elements or managing GUI state.
   - Managing filesystem context or file ingestion.
   - Exporting files, logs, or external artifacts.

 Public API Contract (Post‑Refactor):

   Instance Methods:

     - __init__()
         Inputs: none
         Outputs: AppController instance
         Notes: initializes conversation registry and active ID

     - conversations (property)
         Inputs: none
         Outputs: dict[str, Conversation]

     - active_conversation_id (property getter/setter)
         Inputs: none / str
         Outputs: str or None

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
         Notes: runs persona introduction turn

     - start_new_conversation(persona_name)
         Inputs: persona_name
         Outputs: conversation_id or False
         Notes: full lifecycle: create → switch → initial turn

     - list_conversations()
         Inputs: none
         Outputs: list[str]

     - run_user_turn()
         Inputs: none
         Outputs: none
         Notes: placeholder for future user‑turn abstraction

     - update_chat_display(output_chunk, window_id=None)
         Inputs: output_chunk, window_id
         Outputs: none
         Notes: GUI placeholder

     - update_thinking_display(output_chunk, window_id=None)
         Inputs: output_chunk, window_id
         Outputs: none
         Notes: GUI placeholder

     - integrate_context()
         Inputs: none
         Outputs: none
         Notes: placeholder for context injection logic

   Static Methods:
     - None
"""

import dispatcher
from context_manager import ContextManager
from conversation_manager import ConversationManager
from model_runner import ModelRunner
from utils import Utils


class AppController:
    
    # AppController object initator 
    def __init__(self):
        self._conversations = {}
        self._active_conversation_id = None

    @property
    def conversations(self):
        return self._conversations
    
    @property
    def active_conversation_id(self):
        return self._active_conversation_id
    
    @active_conversation_id.setter
    def active_conversation_id(self, value):
        self._active_conversation_id = value
    
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

            # Normal user message
            ConversationManager.add_user_message(conv, user_input)

            response = ModelRunner.run_conversation(model=conv.model_name, messages=conv.messages, options=conv.options)

            ConversationManager.add_ai_response(conv, response)
            print(f"{conv.persona.capitalize()}:", response.message.content)


    # Creates the conversation and assigns it to the conversations dict with an id
    def create_conversation(self, persona_name):
        conversation = ContextManager.start_conversation(persona_name) 
        conv_id = Utils.generate_conv_id()
        self.conversations[conv_id] = conversation
        return conv_id

    # Entry point for the application 
    def app_run(self):
        self.app_start()
        self.app_repl()

    # Switch the active conversation to the passed conv_id
    def switch_conversation(self, conv_id):
        if conv_id in self.conversations:
            self.active_conversation_id = conv_id
            return True
        
        print(f"No conversation with id: {conv_id}")
        return False
    
    # This will handle getting and clearing the user portion of the conversation
    def run_user_turn():
        pass
    
    #
    def list_conversations(self):
        pass
    
    # First model response (persona introduction)
    def run_initial_conversation_turn(self, conv_id):
        if conv_id not in self.conversations:
            return False
        conversation = self.conversations[conv_id]
        response = ModelRunner.run_conversation(model=conversation.model_name, messages=conversation.messages, options=conversation.options)
        ConversationManager.add_ai_response(conversation, response)
        print(f"{conversation.persona.capitalize()}:", response.message.content)

    
    # Create and start a new conversation
    def start_new_conversation(self, persona_name):
        if persona_name not in ContextManager.personalities:
            return False
        conversation_id = self.create_conversation(persona_name)
        self.switch_conversation(conversation_id)
        self.run_initial_conversation_turn(conversation_id)
        return conversation_id

    # Update the chat display with the response from the model
    def update_chat_display(self, output_chunk, window_id=None):
        pass
    
    # Update the thinking display during streaming output
    def update_thinking_display(self, output_chunk, window_id=None):
        pass

    # Integrate context data into the model prompt when needed
    def integrate_context(self):
        pass
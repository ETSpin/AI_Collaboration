"""
Class: AppController
Author: MORS
Date: 22 MAR 26

Description:
Coordinates the other clases (i.e., ModelRunner, ConversationManager, ContextManager, FileGenerator, and ThinkingDisplay)
so everything doesn't end up in main.py - making the code unreadable and difficult to update later

Usage:
TBD...
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
        conversation = ContextManager.start_conversation(persona_name) 
        conv_id = Utils.generate_conv_id() # need to write this

        self.conversations[conv_id] = conversation #shouldn't this be appended - so you have a running dict of the conversations?
        self.active_conversation_id = conv_id
        #return conv_id

        # First model response (persona introduction)
        response = ModelRunner.run_conversation(
            model=conversation.model_name,
            messages=conversation.messages,
            options=conversation.options
        )

        ConversationManager.add_ai_response(conversation, response)
        print(f"{conversation.persona.capitalize()}:", response.message.content)

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

            response = ModelRunner.run_conversation(
                model=conv.model_name,
                messages=conv.messages,
                options=conv.options
            )

            ConversationManager.add_ai_response(conv, response)
            print(f"{conv.persona.capitalize()}:", response.message.content)

    # Entry point for the application 
    def app_run(self):
        self.app_start()
        self.app_repl()


    # Update the chat display with the response from the model
    def update_chat_display(self, output_chunk, window_id=None):
        pass
    
    # Update the thinking display during streaming output
    def update_thinking_display(self, output_chunk, window_id=None):
        pass

    # Integrate context data into the model prompt when needed
    def integrate_context(self):
        pass
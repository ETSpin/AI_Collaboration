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


class AppController:
    
    # AppController object initator 
    def __init__(self):
        self.context = ContextManager()
        self.conversation_manager = ConversationManager()
        self.runner = ModelRunner()
        self.conversation = None

    # Initialize a new conversation with the selected persona
    def app_start(self, persona_name: str = "pymetheus"):
        self.conversation = self.context.start_conversation(persona_name)

        # First model response (persona introduction)
        response = self.runner.run_conversation(
            model=self.conversation.model_name,
            messages=self.conversation.messages,
            options=self.conversation.options
        )

        self.conversation_manager.add_ai_response(self.conversation, response)
        print(f"{self.conversation.persona.capitalize()}:", response.message.content)

    # Main loop for user interaction
    def app_repl(self):
        while True:
            user_input = input("User: ")

            if not user_input:
                break  # exit on blank input

            # Slash commands
            if user_input.startswith("/"):
                dispatcher.dispatch(user_input[1:], self.conversation)
                continue

            # Normal user message
            self.conversation_manager.add_user_message(self.conversation, user_input)

            response = self.runner.run_conversation(
                model=self.conversation.model_name,
                messages=self.conversation.messages,
                options=self.conversation.options
            )

            self.conversation_manager.add_ai_response(self.conversation, response)
            print(f"{self.conversation.persona.capitalize()}:", response.message.content)

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
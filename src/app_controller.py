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

class AppController:

    # Handles the user's input, small sanity check (very light screening for bad inputs), determines next steps
    def handle_user_input(self, user_message):
        pass

    # Route the request to either the model or the file generator
    def route_to_model_or_file_generator(self, user_message):
        pass

    # Update the chat display with the response from the model
    def update_chat_display(self, output_chunk, window_id=None):
        pass
    
    # Update the thinking display during streaming output
    def update_thinking_display(self, output_chunk, window_id=None):
        pass

    # Integrate context data into the model prompt when needed
    def integrate_context(self):
        pass
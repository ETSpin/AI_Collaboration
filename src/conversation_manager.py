"""
Class: ConversationManager
Author: MORS
Date: 11 APR 26

Description:
Coordinates persona components, model settings, and message flow for a single
conversation. ConversationManager does NOT load personas, store global state,
or interact with external systems beyond calling the model. It assembles the
three components of a conversation (model, context, messages) and manages the
conversation lifecycle.

Responsibilities:
    - Create new conversations using persona/context components
    - Insert system, user, and assistant messages via MessageManager
    - Manage conversation history
    - Switch models or personas (when requested)
    - Apply and validate model settings via ModelManager
    - Call the model and return the AI response (Option A requirement)

Not Responsible For:
    - Loading personalities.json
    - Storing personas
    - Building persona/context components (ContextManager does that)
    - Formatting or styling messages (MessageManager does that)
    - GUI interaction (AppController does that)

Public API Contract:
    Static Methods (conversation lifecycle):
        start_conversation(persona_name, persona_dict, context_components, default_settings, model_name)
        reset_conversation(conversation)

    Static Methods (message flow):
        add_user_message(conversation, input_message)
        add_ai_response(conversation, response)
        add_ai_metadata(conversation, response)

    Static Methods (model interaction):
        run_model(conversation)
        assemble_messages(conversation)

    Static Methods (conversation queries):
        get_model(conversation)
        set_model(conversation, new_model)
        history(conversation)
        get_conversation_info(conversation)
"""

from datetime import datetime, timezone

from conversationobject import ConversationObject
from message_manager import MessageManager
from model_manager import ModelManager
from model_runner import ModelRunner


class ConversationManager:
    # Crete conversation
    @staticmethod
    def start_conversation(persona_name, persona_dict, context_components, default_settings, model_name):
        # Build the system message from the persona components using MessageManager
        system_message = MessageManager.build_system_message(context_components)

        # Build the initial user message
        initial_user_message = MessageManager.build_user_message("Hello.")
        start_messages = [system_message, initial_user_message]

        # Create the conversation object
        conversation = ConversationObject(
            model_name=model_name, messages=start_messages, model_settings=default_settings, persona_name=persona_name, persona_dict=persona_dict, context_components=context_components)

        # Validate settings immediately
        ModelManager.validate_settings(conversation)

        return conversation

    # Convert conversation messages into Ollama's expected format
    @staticmethod
    def assemble_messages(conversation):
        return conversation.messages

    # Accept user's input and append it to the message history
    @staticmethod
    def add_user_message(conversation, input_message):
        MessageManager.append_message(conversation, MessageManager.build_user_message(input_message))

    # Accept the AI's response and append it to the message history
    @staticmethod
    def add_ai_response(conversation, response):
        MessageManager.append_message(conversation, MessageManager.build_assistant_message(response.message.content))
        conversation.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def add_ai_metadata(conversation, response):
        pass

    # Clears all messages except the system prompt.
    @staticmethod
    def reset_conversation(conversation):
        if conversation.messages:
            MessageManager.replace_system_message(conversation, conversation.messages[0])

    # Call the model using ModelRunner and return the response
    @staticmethod
    def run_model(conversation):
        model = conversation.model_name
        settings = conversation.model_settings
        messages = ConversationManager.assemble_messages(conversation)
        response = ModelRunner.run_conversation(model, messages, settings)

        return response

    # Return the model name for this conversation
    @staticmethod
    def get_model(conversation):
        return conversation.model_name

    # Set the model name (validation can go here later)
    @staticmethod
    def set_model(conversation, new_model):
        conversation.model_name = new_model

    # Return the conversation history
    @staticmethod
    def history(conversation):
        return conversation.messages

    # Return the overview of this conversation
    @staticmethod
    def get_conversation_info(conversation):
        return str(conversation)

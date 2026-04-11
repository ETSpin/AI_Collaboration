"""
Class: MessageManager
Author: MORS
Date: 11 APR 26

Description:
Manages the message-history component of a ConversationObject. MessageManager is responsible ONLY for constructing, normalizing,
and manipulating message dictionaries. It does NOT interact with models, personas, or conversation lifecycle logic.

Responsibilities:
    - Build system, user, and assistant message dictionaries
    - Normalize message structure for consistency
    - Append messages to a conversation's message history
    - (Future) Trim or prune message history based on token limits
    - (Future) Handle file-context blocks as system messages

Not Responsible For:
    - Persona or context construction (ContextManager)
    - Model settings or validation (ModelManager)
    - Sending conversations to the model (ConversationManager)
    - Maintaining conversation registry (ConversationManager)
    - GUI or user interaction (AppController)

Public API Contract:
    Static Methods (message construction):
        build_system_message(context_components) -> dict
        build_user_message(text) -> dict
        build_assistant_message(text) -> dict

    Static Methods (message normalization):
        normalize_message(message_dict) -> dict

    Static Methods (message history operations):
        append_message(conversation, message_dict)
        replace_system_message(conversation, message_dict)
        trim_history(conversation, max_tokens) -> None

    Static Methods (context injection):
        build_file_context_block(file_data) -> dict
        inject_context_block(conversation, block_dict)
"""


class MessageManager:
    # Build a system message from persona/context components
    @staticmethod
    def build_system_message(context_components):
        prompt_prefix = context_components.get("prompt_prefix", "").strip()
        personality = context_components.get("personality", "").strip()
        rules = context_components.get("rules", "").strip()

        content = f"{prompt_prefix}\n\n{personality}\n\nRules:\n{rules}"

        return MessageManager.normalize_message({"role": "system", "content": content})

    # Build a user message from their input text
    @staticmethod
    def build_user_message(text):
        return MessageManager.normalize_message({"role": "user", "content": text})

    # Build the AI "assistant" message
    @staticmethod
    def build_assistant_message(text):
        return MessageManager.normalize_message({"role": "assistant", "content": text})

    # Ensure message dict has required fields and clean formatting
    @staticmethod
    def normalize_message(message_dict):
        if "role" not in message_dict:
            raise ValueError("[MessageManager] Message missing required field: 'role'")
        if "content" not in message_dict:
            raise ValueError("[MessageManager] Message missing required field: 'content'")

        role = str(message_dict["role"]).strip()
        content = str(message_dict["content"]).strip()

        return {"role": role, "content": content}

    # Append a normalized message to the conversation history
    @staticmethod
    def append_message(conversation, message_dict):
        normalized = MessageManager.normalize_message(message_dict)
        conversation._messages.append(normalized)

    # Replace the first (system) message in the conversation - enables conversation context updates
    @staticmethod
    def replace_system_message(conversation, message_dict):
        normalized = MessageManager.normalize_message(message_dict)

        if not conversation._messages:
            conversation._messages = [normalized]
        else:
            conversation._messages[0] = normalized

    # Placeholder for future token-budget logic
    @staticmethod
    def trim_history(conversation, max_tokens):
        return

    # Build a system-style block for file context
    @staticmethod
    def build_file_context_block(file_data):
        content = f"[FILE CONTEXT]\n{file_data.strip()}"
        return MessageManager.normalize_message({"role": "system", "content": content})

    # Insert a context block immediately after the primary system message
    @staticmethod
    def inject_context_block(conversation, block_dict):
        normalized = MessageManager.normalize_message(block_dict)

        if not conversation._messages:
            conversation._messages = [normalized]
            return

        conversation._messages.insert(1, normalized)

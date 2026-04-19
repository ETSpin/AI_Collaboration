"""
File: conversationobject.py
Author: MORS
Date: 28 MAR 26

Description:
Represents a single conversational session between the user and an AI persona.
Stores all stateful information required to run, resume, serialize, or inspect a
conversation. Acts as a structured container for model configuration, message
history, metadata, and lifecycle timestamps. A ConversationObject holds the
three components required to execute a model turn:

    1. model_settings   (from ModelManager)
    2. context_components (from ContextManager)
    3. message_history  (from MessageManager)

It is immutable in structure but mutable in content (messages grow, metadata
updates, timestamps change). It does NOT run the model and does NOT modify
its own messages.

Responsibilities:
    - Store the model name used for this conversation.
    - Store the externally assigned conversation_id.
    - Hold context_components (prompt_prefix, personality, rules).
    - Hold model_settings (temperature, top_p, num_ctx, etc.).
    - Store the message history list (role/content dicts).
    - Track creation and update timestamps.
    - Store metadata, token counts, and optional conversation title.
    - Store the assistant's prompt_name.
    - Provide read-only accessors for conversation state.
    - Provide readable __str__ and __len__ helpers for debugging.

Not Responsible For:
    - Running the model (ConversationManager does that).
    - Adding or modifying messages (MessageManager does that).
    - Generating conversation IDs (AppController/Utils).
    - Managing GUI or CLI output.
    - Loading personas or building context (ContextManager).
    - Managing or validating model settings (ModelManager).

Public API Contract:

    Constructor:
        __init__(model_name, conversation_id=None, context_block=None,
                 persona_name=None, persona_dict=None, model_settings=None,
                 messages=None, context_components=None, prompt_name="AI agent:")

    Properties:
        model_name (get/set)
        model_settings (get/set)
        context_block (get/set)
        messages (get)
        conversation_id (get/set)
        prompt_name (get/set)
        created_at (get/set)
        updated_at (get/set)
        metadata (get/set)
        token_count (get/set)
        title (get/set)

    Special Methods:
        __len__() → number of message turns
        __str__() → human-readable summary

"""

from datetime import datetime, timezone


class ConversationObject:
    # Represents a fully assembled conversational state at a single point in time.
    def __init__(self, model_name, conversation_id=None, context_block=None, persona_name=None, persona_dict=None, model_settings=None, messages=None, context_components=None, prompt_name="AI agent:"):
        self._model_name = model_name
        self._conversation_id = conversation_id
        self._model_settings = model_settings if model_settings is not None else {}
        
        self.persona_name = persona_name
        self.persona_dict = persona_dict

        self.context_components = context_components or {}
        
        self._messages = messages if messages is not None else []
        self._created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self._updated_at = None
        self._metadata = {}
        self._title = None #(summary of the conversation)
        self._prompt_name = prompt_name

        self.files = {}          # { "src/gui.py": {"size": 1234, "chunks": [chunk1, chunk2]} }
        self.files_directory_summary = ""  # A formatted tree summary

        self.tokens_model_max = 0
        
    # -------------------------
    # Properties
    # -------------------------
    @property
    def model_name(self):
        return self._model_name

    @model_name.setter
    def model_name(self, value):
        self._model_name = value

    @property
    def model_settings(self):
        return self._model_settings

    @model_settings.setter
    def model_settings(self, value):
        self._model_settings = value

    @property
    def context_block(self):
        return self._context_block

    @context_block.setter
    def context_block(self, value):
        self._context_block = value

    @property
    def messages(self):
        return self._messages

    @property
    def conversation_id(self):
        return self._conversation_id

    @conversation_id.setter
    def conversation_id(self, value):
        self._conversation_id = value

    @property
    def prompt_name(self):
        return self._prompt_name

    @prompt_name.setter
    def prompt_name(self, value):
        self._prompt_name = value

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = value

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        self._updated_at = value

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def token_count(self):
        return self._token_count

    @token_count.setter
    def token_count(self, value):
        self._token_count = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # -------------------------
    # Helpers
    # -------------------------
    # Returns the number of "turns" in the conversation
    def __len__(self):
        return len(self.messages)

    # Basic printout for a conversation object
    def __str__(self):
        lines = []
        lines.append(f"Conversation(model='{self._model_name}')")
        lines.append(f"  prompt_name: {self._prompt_name}")
        lines.append(f"  created_at: {self._created_at}")
        lines.append(f"  updated_at: {self._updated_at}")
        lines.append(f"  title: {self._title}")
        lines.append(f"  turns: {len(self._messages)}")
        lines.append("  messages:")

        for i, msg in enumerate(self._messages, start=1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            preview = content if isinstance(content, str) and len(content) <= 80 else (
                content[:77] + "..." if isinstance(content, str) else str(content)
            )
            lines.append(f"    {i}. {role}: {preview}")

        return "\n".join(lines)
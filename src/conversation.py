"""
Class: conversation
Author: MORS
Date: 28 MAR 26

Description:
This is the conversation class -- it will enable the creation of a conversation object that contains
messages, model name, and other data for each conversation

Usage:
As a container class, I am exposing the 
"""
from datetime import datetime, timezone


class Conversation:
    
    # Initiates a conversation object
    def __init__(self, model_name, messages=None, model_options=None):
        self._model_name = model_name
        self._messages = messages if messages is not None else []
        self._created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._options = model_options

        self._conversation_id = None
        self._persona = None # This will set the model's temperature sampling parameter (low is more literal, high is more creative)
        self._updated_at = None
        self._metadata = []
        self._token_count = 0
        self._title = None #(summary of the conversation)
        

    @property
    def model_name(self):
        return self._model_name

    @model_name.setter
    def model_name(self, value):
        self._model_name = value

    # Returns the conversation history as an editable object
    @property
    def messages(self):
        return self._messages

    @property
    def options(self):
        return self._options

    @options.setter
    def persona(self, value):
        self._options = value


    @property
    def persona(self):
        return self._persona

    @persona.setter
    def persona(self, value):
        self._persona = value

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

    # Returns the number of "turns" in the conversation
    def __len__(self):
        return len(self.messages)

    # Basic printout for a conversation object
    def __str__(self):
        lines = []
        lines.append(f"Conversation(model='{self._model_name}')")
        lines.append(f"  created_at: {self._created_at}")
        lines.append(f"  updated_at: {self._updated_at}")
        lines.append(f"  persona: {self._persona}")
        lines.append(f"  title: {self._title}")
        lines.append(f"  turns: {len(self._messages)}")
        lines.append("  messages:")

        # Show each message in a compact, readable way
        for i, msg in enumerate(self._messages, start=1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Truncate long content for readability
            preview = content
            if isinstance(content, str) and len(content) > 80:
                preview = content[:77] + "..."

            lines.append(f"    {i}. {role}: {preview}")

        return "\n".join(lines)
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

class Conversation:
    
    # Initiates a conversation object
    def __init__(self, model_name, messages=None):
        self._model_name = model_name
        self._messages = messages if messages is not None else []
        
        self._conversation_id = None
        self._persona = None
        self._created_at = None
        self._updated_at = None
        self._metadata = {}
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

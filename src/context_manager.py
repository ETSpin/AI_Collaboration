"""
Class: ContextManager
Author: MORS
Date: 22 MAR 26 (Refactored 11 APR 26)

Description:
Pure static utility class for working with persona definitions.
ContextManager does NOT load JSON, store state, or create conversations.
All persona data is provided externally - by AppController(usually).

Responsibilities:
    - Validate persona definitions
    - Retrieve persona metadata
    - List available personas
    - Build structured context components for ConversationManager
    - Provide default model settings for a persona

Not Responsible For:
    - Loading personalities.json
    - Storing personas
    - Creating Conversation objects
    - Injecting context into conversations
    - Handling file uploads or external tools

Public API Contract:
    Static Methods (persona validation):
        validate_persona(persona_key, persona_dict) -> bool

    Static Methods (persona retrieval):
        get_persona(personas_dict, name) -> dict | None
        list_personas(personas_dict) -> list

    Static Methods (persona components):
        get_default_settings(persona_dict) -> dict
        get_model_name(persona_dict) -> str
        get_prompt_prefix(persona_dict) -> str
        get_personality_text(persona_dict) -> str
        get_rules(persona_dict) -> str
        build_context_components(persona_dict) -> dict
"""

import copy

import tiktoken


class ContextManager:
    # Ensures a persona is in the correct format and contains all required fields
    @staticmethod
    def validate_persona(key, data):
        required_top_level_fields = ["name", "prompt_prefix", "model", "personality", "rules", "defaults", "description"]

        for field in required_top_level_fields:
            if field not in data:
                raise ValueError(f"[ContextManager] Persona '{key}' missing field '{field}'")

        required_defaults = ["num_ctx", "temperature", "top_p", "top_k", "repeat_penalty"]

        for field in required_defaults:
            if field not in data["defaults"]:
                raise ValueError(f"Persona '{key}' missing default setting: '{field}'")

    # Returns a deep copy of the persona definition
    @staticmethod
    def get_persona(personas, name):
        if name not in personas:
            return None
        return copy.deepcopy(personas[name])

    # Returns a sorted list of persona metadata: [{ "key": ..., "name": ..., "description": ... }]
    @staticmethod
    def list_personas(personas: dict):
        persona_list = []

        for key, persona_data in personas.items():
            persona_list.append({"key": key, "name": persona_data["name"], "description": persona_data["description"]})
        return sorted(persona_list, key=lambda item: item["name"].lower())

    @staticmethod
    def get_default_settings(persona: dict):
        return copy.deepcopy(persona["defaults"])

    @staticmethod
    def get_model_name(persona: dict):
        return persona["model"]

    @staticmethod
    def get_prompt_prefix(persona: dict):
        return persona["prompt_prefix"]

    @staticmethod
    def get_personality_text(persona: dict):
        return persona["personality"]

    @staticmethod
    def get_rules(persona: dict):
        return persona["rules"]

    # Returns a structured dictionary containing the persona's personality, rules, and prompt prefix.
    @staticmethod
    def build_context_components(persona):
        return {"prompt_prefix": persona["prompt_prefix"], "personality": persona["personality"], "rules": persona["rules"]}
    
    # Returns a fairly accurate estimate of tokens that would be used for a given text str
    def count_tokens(text):
        if not text:
            return 0
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

"""      
# Create and return a fully-initialized Conversation object based on the selected personality profile.
    @staticmethod
    def start_conversation(persona_name: str):
        # Gets the personality profile from the dictionary of personalities -- returns an error it doesn't exist
        persona = ContextManager.personalities.get(persona_name)
        if persona is None:
            raise ValueError(f"Unknown personality: {persona_name}")

        # Get the model and its options - based on the personality selected
        model_name = persona.get("model")
        model_options = {
            "num_ctx": persona.get("num_ctx"),
            "temperature": persona.get("temperature"),
            "top_p": persona.get("top_p"),
            "top_k": persona.get("top_k"),
            "repeat_penalty": persona.get("repeat_penalty"),
        }
        # dictionary comprehension to remove blanks from the model_options dictionary
        model_options = {k: v for k, v in model_options.items() if v not in ("", None)}


        # Create the base of the conversation with the configuration message
        start_messages = [
            {
                "role": "system",
                "content": persona.get("personality") or ""
            },
            {
                "role": "user",
                "content": "Hello."
            }
        ]

        # Create and return the Conversation object
        conversation = Conversation(model_name=model_name,messages=start_messages,model_options=model_options)

        # Update the conversation personality
        conversation.persona = persona_name
        return conversation 


    # This fucntion updates the starting conversation from the system with new context
    # This should prevent issues with adding system context after starting a conversation
    @staticmethod
    def inject_context(conversation, block):
        system_msg = conversation.messages[0]
        system_msg["content"] += "\n\n" + block["contents"]
        conversation.messages[0] = system_msg

"""

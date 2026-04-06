"""
Class: ContextManager
Author: MORS
Date: 22 MAR 26

Description:
Handles any user provided files and an ability to import data from a library
- Will likley also handle other tool(s) or methods for the model to be able to get additional information (web, other local tools, etc.)

Usage:
TBD...

"""
import copy
import json
from pathlib import Path

from conversation import Conversation


class ContextManager:
    def __init__(self):
        self._persona_file_path = "./src/personalities.json" #we'll look at cleaning this up with another directory later
        self._personas = []
        
        self.load_personas()

    # Load the persona file from the persona
    def load_personas(self):
        path = Path(self._persona_file_path)
        if not path.exists():
            print(f"Persona file not found: {path}")
            return False

        with path.open("r", encoding="utf-8") as f:
            temp_personas_dict = json.load(f)

        if "_comment" in temp_personas_dict:
            del temp_personas_dict["_comment"]

        for persona_key, persona_data in temp_personas_dict.items():
            if not self.validate_persona(persona_key, persona_data):
                print(f"Validation failed for persona '{persona_key}'")
                return False
        
        self._personas = temp_personas_dict
        return True

    # Get the Personal from the loaded personas
    def get_persona(self, name):
        if name not in self._personas:
            print(f"[ContextManager] Persona {name} not found in available personas")
            return None
        return copy.deepcopy(self._personas[name])
    
    # Helper function - returns a list of the available personas - along with their descriptions
    def list_personas(self):
        persona_list = []

        for key, data in self._personas.items():
            persona_list.append({"key": key,"name": data["name"], "description": data["description"]})

        print(f"[ContextManager] No Error just info --- Available personas: {[p['key'] for p in persona_list]}")
        return sorted(persona_list, key=lambda p: p["name"].lower())  # this is a list of keys and descriptions in self._personas

    # Helper function - ensures the personas are in the correct format -- will save time later
    def validate_persona(self, key, data):
        required_top_level_fields = ["name", "prompt_prefix", "model", "personality", "rules", "defaults", "description"]

        for field in required_top_level_fields:
            if field not in data:
                print(f"Persona '{key}' missing field '{field}'")
                return False

        required_defaults = ["num_ctx", "temperature", "top_p","top_k", "repeat_penalty"]

        for field in required_defaults:
            if field not in data["defaults"]:
                print(f"Persona '{key}' missing default requirement: '{field}'")
                return False

        return True

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
    
    """Accept user's file input """
    def build_prompt(self, input_file):
        pass
       
    """Accept user's file input """
    def accept_file_upload(self, input_file):
        pass

    """Determine the type of file uploaded by the user """
    def detect_file_type(self, input_file):
        pass

    """Actually extract data from the uploaded file"""
    def extract_data(self, input_file):
        pass

    """Store the the extracted data from the file for the model to be able to access"""
    def store_context_data(self, data):
        pass

    """Returns a list of the user pushed files being used in the context"""
    def get_context_data(self):
        pass

    """Remove the the extracted data from the model's context for future 'thinking' """
    def remove_context_data(self, data):
        pass

    """Load additional context data from a local library or repository"""
    def load_library_files(self, directory):
        pass

    """Returns a list of the local library or repository items used for additional context"""
    def get_library_list(self):
        pass

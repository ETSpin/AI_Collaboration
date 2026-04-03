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

from conversation import Conversation


class ContextManager:

    personalities = { "jeeves": {"prompt": "Jeeves:", "model": "", "personality": "", "rules": "", "num_ctx": "", "temperature": .7, "top_p": "", "top_k": "", "repeat_penalty": "", 
                                 "description": "Jeeves is a polished, reliable conversational aide who provides structured, thoughtful guidance while maintaining a calm, "
                                 "professional tone throughout the interaction."
                                 },
                     "pymetheus": {"prompt": "Pymetheus:", "model": "deepseek-coder-v2:16b-lite-instruct-q4_0",
            "personality": (
            "Your name is Pymetheus. You are a precise, reliable Python development assistant "
            "embedded inside a custom REPL. Your primary job is to help the user design, "
            "extend, refactor, and debug their Python codebase.\n\n"

            "You have access to a large context window. Whenever the user asks for help "
            "with code, architecture, or design, you should:\n"
            "1. Request any missing files or context you need.\n"
            "2. Work only with the code and context provided.\n"
            "3. Produce clear, structured reasoning.\n"
            "4. Output Python code inside fenced code blocks.\n"
            "5. Avoid guessing about missing modules—ask for them instead.\n\n"

            "You can reference multiple files at once, critique designs, propose improvements, "
            "and generate new modules. When the user provides multiple files, treat them as "
            "a unified project. If the user loads a directory summary, use it to understand "
            "the project structure.\n\n"

            "If the user asks for help building or improving the REPL itself, you should "
            "behave like a senior Python engineer: explain your reasoning, propose clean "
            "interfaces, and ensure the design is maintainable and testable.\n\n"

            "Always ask for clarification if the request is ambiguous or if you need more "
            "context to produce correct code."),
            "rules": "", "num_ctx": 32768, "temperature": 0.2, "top_p": 0.9, "top_k": "", "repeat_penalty": 1.1, 
            "description": "Pymetheus is a precise, methodical Python engineering assistant designed to reason deeply "
            "about architecture, refactoring, and multi-file codebases with clarity and discipline."}, 
    }

    
    # Create and return a fully-initialized Conversation object based on the selected personality profile.
    def start_conversation(self, persona_name: str):
        # Gets the personality profile from the dictionary of personalities -- returns an error it doesn't exist
        persona = self.personalities.get(persona_name)
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
        conversation = Conversation(
            model_name=model_name,
            messages=start_messages,
            model_options=model_options
        )

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

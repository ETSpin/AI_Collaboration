"""
Class: ModelRunner
Author: MORS
Date: 22 MAR 26

Description:
This  class that will hold all of the model interactions between Ollama and Python.
- will handle single turn or streaming output (conversations in Ollama are basically single_turn, with history reloaded)

Usage:
TBD...

"""

class ModelRunner:
    
    """Select a model """
    def set_model(self, model_name):
        pass

    """Run a single AI call"""
    def run_single_turn(self, input_text):
        pass

    """What is the AI 'thinking' -- stream it's output token-by-token"""
    def stream_partial_output(self, callback):
        pass

    """Reset or reinitialize the model as needed"""
    def reset_model_state(self):
        pass

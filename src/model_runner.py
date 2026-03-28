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
from ollama import chat


class ModelRunner:
    
    """Select a model """
    def set_model(self, model_name):
        pass

    """Run a single AI call"""
    def run_single_turn(self, model, input_text):
        messages = [
        {
            "role": "user",
            "content": input_text,
        },
                    ]

        response = chat(model, messages=messages)
        print(response.message.content)

    '''Run a multi response conversation'''
    def run_conversation(self, model, messages):
        response = chat(model, messages)
        return response

    """What is the AI 'thinking' -- stream it's output token-by-token"""
    def stream_partial_output(self, callback):
        pass

    """Reset or reinitialize the model as needed"""
    def reset_model_state(self):
        pass

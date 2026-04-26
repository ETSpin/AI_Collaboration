"""
File: model_runner.py
Author: MORS
Date: 22 MAR 26

Description:
Handles all model interactions between Python and the Ollama runtime. Provides
single-turn, multi-turn, and (future) streaming execution paths. Does not manage
conversation state, defaults, or persona logic. Operates strictly as a thin
execution layer over the Ollama API.

Responsibilities:
    - Execute single-turn model calls.
    - Execute multi-turn conversation calls using message history.
    - Provide hooks for future streaming output.
    - Provide hooks for resetting or reinitializing model state.

Not Responsible For:
    - Managing conversation history (MessageManager).
    - Managing model settings or validation (ModelManager).
    - Selecting or switching models (ConversationManager).
    - Loading personas or context (ContextManager).
    - GUI or REPL behavior (AppController / Gui).

Public API Contract:

    Instance Methods:
        - set_model(model_name)
            Inputs: model name (str)
            Outputs: None
            Notes: Placeholder for future model selection logic.

        - stream_partial_output(callback)
            Inputs: callback function
            Outputs: None
            Notes: Placeholder for future streaming token output.

        - reset_model_state()
            Inputs: none
            Outputs: none
            Notes: Placeholder for future model reset logic.

    Static Methods:
        - run_single_turn(model, input_text)
            Inputs: model name, user text
            Outputs: Ollama response object
            Notes: Executes a single user→model turn.

        - run_conversation(model, messages, options)
            Inputs: model name, message list, model options
            Outputs: Ollama response object
            Notes: Executes a multi-turn conversation using full message history.

"""

from ollama import chat


class ModelRunner:
    # Select a model
    def set_model(self, model_name):
        pass

    # Run a single AI call
    @staticmethod
    def run_single_turn(model, input_text):
        messages = [{"role": "user","content": input_text,},]

        response = chat(model, messages=messages)
        print(response.message.content)

    # Run a multi response conversation
    @staticmethod
    def run_conversation(model, messages, options):
        final_response = ""
        response = chat(model=model, messages=messages, options=options)
        return response

    # Run a multi-turn conversation, but with streaming turned on
    def run_conversation_streaming(model, messages, options, callback):
        response = chat(model=model, messages=messages, stream=True, options=options)
        return response


    # What is the AI 'thinking' -- stream it's output token-by-token
    def stream_partial_output(self, callback):
        pass

    # Reset or reinitialize the model as needed
    def reset_model_state(self):
        pass

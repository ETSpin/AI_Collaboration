"""
File: main.py
Author: MORS
Date: 21 MAR 26

Description:
AI experimentation with Ollama and Python

Initial examples/research from https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide 

Usage:

"""
from ollama import chat

import dispatcher
from context_manager import ContextManager
from conversation_manager import ConversationManager
from model_runner import ModelRunner


def main():

    contextmgr = ContextManager()
    runner = ModelRunner()
    manager = ConversationManager()

    # This makes the AI model start the conversation
    conversation = contextmgr.start_conversation("pymetheus")
    response = chat(model=conversation.model_name, messages=conversation.messages, options=conversation.options)
    print(f"{conversation.persona.capitalize()}:", response.message.content)

    # This is the loop where the actual conversation takes place
    while True:
        user_input = input("User: ")
        if not user_input:
            break # exit the loop if the user provides a blank input
        elif not user_input[0] == "/":
            manager.add_user_message(conversation, user_input)
            response = runner.run_conversation(model=conversation.model_name, messages=conversation.messages, options=conversation.options)
            manager.add_ai_response(conversation, response)
            print(f"{conversation.persona.capitalize()}:", response.message.content)
        else:
            dispatcher.dispatch(user_input[1:], conversation)


if __name__ == '__main__':
    main()

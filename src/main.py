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
from conversation import Conversation
from conversation_manager import ConversationManager
from model_runner import ModelRunner


def main():

    start_conversation = [
        {"role":"system", "content":"You are named Jeeves and are a useful helper."},
        {"role": "user", "content" : "Hello"},
    ]

    conversation = Conversation("llama3.2:latest",start_conversation) 
    runner = ModelRunner()
    manager = ConversationManager()

    # This makes the AI model start the conversation
    response = chat(conversation.model_name, conversation.messages)
    print("Jeeves:", response.message.content)

    # This is the loop where the actual conversation takes place
    while True:
        user_input = input("User: ")
        if not user_input:
            break # exit the loop if the user provides a blank input
        elif not user_input[0] == "/":
            manager.add_user_message(conversation, user_input)
            response = runner.run_conversation(conversation.model_name, conversation.messages)
            manager.add_ai_response(conversation, response)
            print("Jeeves:", response.message.content)
        else:
            dispatcher.dispatch(user_input[1:], conversation)


if __name__ == '__main__':
    main()

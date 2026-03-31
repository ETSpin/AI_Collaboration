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
    {
        "role": "system",
        "content": (
            "Your name is Jeeves. You are a precise, reliable Python development assistant "
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
            "context to produce correct code."
        )
    },
    {
        "role": "user",
        "content": "Hello Jeeves."
    }
]

    conversation = Conversation("deepseek-coder-v2:16b-lite-instruct-q4_0",start_conversation) 
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

"""
File: main.py
Author: MORS
Date: 21 MAR 26

Description:
AI experimentation with Ollama and Python

Initial examples/research from https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide 

Usage:

"""
import ollama

#from model_runner import ModelRunner


def main():
    # Question = ModelRunner()
    model_name = "llama3.2:latest" # I know I downloaded this model

    conversation = [
        {"role":"system", "content":"You are named Jeeves and are a useful helper."},
        {"role": "user", "content" : "Hello"},
    ]

    # This makes the AI model start the conversation
    response = ollama.chat(model=model_name, messages = conversation)
    print("Jeeves:", response.message.content)

    # This is the loop where the actual conversation takes place
    while True:
        user_input = input("User: ")
        if not user_input:
            break # exit the loop if the user provides a blank input

        conversation.append({"role": "user", "content" : user_input})
        response = ollama.chat(model=model_name, messages = conversation)
        aianswer = response.message.content
        print("Jeeves:", aianswer)
        conversation.append({"role": "assistant", "content" : aianswer})


if __name__ == '__main__':
    main()

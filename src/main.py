"""
File: main.py
Author: MORS
Date: 21 MAR 26

Description:
AI experimentation with Ollama and Python

Usage:

"""
from ollama import chat


def main():
    messages = [
        {
            "role": "user",
            "content": "funny question, can a swallow carry a coconut",
        },
    ]

    response = chat(model="llama3.2:latest", messages=messages)
    print(response.message.content)

if __name__ == '__main__':
    main()

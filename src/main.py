"""
File: main.py
Author: MORS
Date: 21 MAR 26

Description:
AI experimentation with Ollama and Python

Initial examples/research from https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide 

Usage:

"""

from app_controller import AppController

# from context_loader import ContextLoader
# from context_manager import ContextManager


def main():
    AppController().app_run()

    # cm = ContextManager()
    # loader = ContextLoader()

    # conv = cm.start_conversation("pymetheus")

    # # TEMPORARY TEST
    # loader.directory_to_context(conv, "./src")

    # print("\n=== SYSTEM MESSAGE AFTER LOADING ===\n")
    # print(conv.messages[0]["content"])

if __name__ == '__main__':
    main()
"""
File: dispatcher.py
Author: MORS
Date: 20 Dec 25

Description:
    Command dispatcher This module receives raw command strings from the main event loop, parses them into their constituent
    components (command, arguments, and flags), and routes them to the appropriate handler within the system.

    The dispatcher is intentionally lightweight and modular. Each command handler is responsible for validating its own arguments and flags,
    enforcing defaults, and returning a human-readable response string suitable for display in the GUI output window.

Usage:
    TBD...
"""
import argparse
import shlex

from conversation_manager import ConversationManager as cm

key_words = {
    "get": 
    { 
        "description": "Displays information about the current model or conversation",
        "args": 
        [
            {"flags": ["what"], "options": {"choices" : ["model", "conversation","temp"],"help": "Display information about the current conversation or model"}},
        ],
        "handler": lambda args: display(args.what, args.conversation)
    },
    
    "set":
    {
        "description": "Change aspects of the current model or conversation",
        "args": 
        [
            {"flags": ["what"], "options": {"choices" : ["model", "temp"], "help": "Change the model being used for the current conversation"}},
            {"flags": ["value"], "options": {"help": "The new value of the paramater"}},
        ],
        "handler": lambda args: update(args.what, args.value, args.conversation)
    },

    "show":
    {
        "description": "Show features from the Ollama CLI",
        "args": 
        [
            {"flags": ["what"], "options": {"choices" : ["models"], "help": "Showw a list of the available models"}},
        ],
        "handler": lambda args: available_models()
    },

        "reset":
    {
        "description": "Resets the current conversation",
        "args": [],
        "handler": lambda args: cm.reset_conversation(args.conversation)
    },

    "help": {
        "description": "Show a list of available commands",
        "args": [],
        "handler": lambda args: help_command()
    },
}

def dispatch(cmd, conversation):
    args = shlex.split(cmd)
    keyword = args[0]
    tokens = args[1:]
    if keyword in key_words.keys():
        cmdparser = parserbuilder(keyword)

        try:
            arguments = cmdparser.parse_args(tokens)
            arguments.conversation = conversation
            key_words[keyword]["handler"](arguments)
        except SystemExit:
            pass

    else:
        print(f"{cmd} does not exist")
    
    
def display(attribute, conversation):
    if attribute == "model":
        print(cm.get_model(conversation))

    elif attribute == "conversation":
        print(cm.get_conversation_info(conversation))

    elif attribute == "temp":
        print(cm.get_temperature(conversation))

    else:
        print(f"Unknown attribute: {attribute}")


def update(attribute, value, conversation):
    if attribute == "model":
        cm.set_model(conversation, value)

    elif attribute == "temp":
        cm.set_temperature(conversation, value)

    else:
        print(f"Unknown attribute: {attribute}")


def available_models():
    print(cm.get_available_models())


def help_command():
    print ("Overview of Possible Commands")
    for cmd_word in key_words:
        print(f"{cmd_word} - ", key_words[cmd_word]["description"])


def parserbuilder(cmdword):
    parser = argparse.ArgumentParser(prog = cmdword, add_help=False)
    parser.add_argument("-h", "--help", action="help", help="display this help message (program continues)")
    arg_definitions = key_words[cmdword]["args"]
    for arg_def in arg_definitions:
        names = arg_def["flags"]
        metadata = arg_def["options"]
        parser.add_argument(*names, **metadata)
    return parser


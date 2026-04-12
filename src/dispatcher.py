"""
File: dispatcher.py
Author: MORS
Date: 20 DEC 25

Description:
Lightweight command-routing layer for the application. The dispatcher receives
raw command strings from the AppController (typically via the CLI REPL), parses
them into structured arguments, and forwards them to the appropriate subsystem.
Supports two command namespaces:
    • System commands ("/")
    • Conversation commands ("-")
Performs no business logic; only parses, validates, and routes commands.

Responsibilities:
    - Tokenize raw command strings using shlex.
    - Identify the command namespace (system vs. conversation).
    - Build argparse parsers dynamically based on keyword metadata.
    - Validate arguments and flags for each command.
    - Route parsed arguments to the appropriate handler function.
    - Provide help listings for both system and conversation commands.
    - Surface errors cleanly without terminating the application.

Not Responsible For:
    - Mutating conversation state (ConversationManager handles this).
    - Running models or modifying model settings (ModelManager / AppController).
    - Loading files or directories into context (ContextLoader).
    - Monitoring system resources (RuntimeMonitor).
    - Installing or uninstalling models (Utils / ModelManager).
    - Rendering GUI output or managing GUI state.

Public API Contract:

    System Command Entry Point:
        - system_dispatch(cmd, conversation)
            Inputs: raw command string (no leading "/"), Conversation object
            Outputs: none
            Notes: Parses and routes system-level commands.

    Conversation Command Entry Point:
        - conversation_dispatch(cmd, conversation)
            Inputs: raw command string (no leading "-"), Conversation object
            Outputs: none
            Notes: Parses and routes conversation-level commands.

    System Handlers:
        - system_display(attribute, conversation)
        - system_update(attribute, value, conversation)
        - system_show_model_info(attribute)
        - system_install_model(attribute)
        - system_uninstall_model(attribute)
        - system_show_stats(attribute)
        - system_help_command()

    Conversation Handlers:
        - load_file(conversation, path)
        - load_directory(conversation, path)
        - conversation_help()

    Parser Builders:
        - system_parserbuilder(cmdword)
        - conversation_parserbuilder(cmdword)
 
"""
import argparse
import os
import shlex
import subprocess
import time

from context_loader import ContextLoader
from conversation_manager import ConversationManager
from model_manager import ModelManager
from runtime_monitor import RuntimeMonitor
from utils import Utils as utils

system_key_words = {
    "get": 
    { 
        "description": "Displays information about the current model or conversation",
        "args": 
        [
            {"flags": ["what"], "options": {"choices" : ["model", "conversation","temp"],"help": "Display information about the current conversation or model"}},
        ],
        "handler": lambda args: system_display(args.what, args.conversation)
    },
    
    "set":
    {
        "description": "Change aspects of the current model or conversation",
        "args": 
        [
            {"flags": ["what"], "options": {"choices" : ["model", "temp"], "help": "Change the model being used for the current conversation"}},
            {"flags": ["value"], "options": {"help": "The new value of the paramater"}},
        ],
        "handler": lambda args: system_update(args.what, args.value, args.conversation)
    },

    "show":
    {
        "description": "Show features from the Ollama CLI",
        "args": 
        [
            {"flags": ["what"], "options": {"choices" : ["downloaded", "available", "running"], "help": "Show downloaded models, models available to download, and running models"}},
        ],
        "handler": lambda args: system_show_model_info(args.what)
    },

    "install":
    {
        "description": "Download and install an AI model from the Ollama website",
        "args": 
        [
            {"flags": ["what"], "options": {"help": "Downloads and installs a model through the Ollama CLI"}},
        ],
        "handler": lambda args: system_install_model(args.what)
    },

    "uninstall":
    {
        "description": "Uninstalls an AI model from the local system",
        "args": 
        [
            {"flags": ["what"], "options": {"help": "Uninstalls an installed model through the Ollama CLI"}},
        ],
        "handler": lambda args: system_uninstall_model(args.what)
    },

    "stats": 
    {
        "description": "Display system resource usage (CPU, memory, GPU, VRAM, or live feed)",
        "args": 
        [
            {"flags": ["what"], "options": {"choices": ["cpu", "memory", "gpu", "vram", "all", "live"],"help": "Which system statistic(s) to display"}},
        ],
    "handler": lambda args: system_show_stats(args.what)
    },

    "reset":
    {
        "description": "Resets the current conversation",
        "args": [],
        "handler": lambda args: ConversationManager.reset_conversation(args.conversation)
    },

    "help": {
        "description": "Show a list of available commands",
        "args": [],
        "handler": lambda args: system_help_command()
    },
}

def system_dispatch(cmd, conversation):
    args = shlex.split(cmd)
    if not args:
        print("No system command given")
        return
    
    keyword = args[0]
    tokens = args[1:]

    if keyword not in system_key_words.keys():
        print(f"Unown system command: {keyword}")
        return
        
    cmdparser = system_parserbuilder(keyword)

    try:
        arguments = cmdparser.parse_args(tokens)
        arguments.conversation = conversation
        system_key_words[keyword]["handler"](arguments)
    except SystemExit:
        pass
    
def system_display(attribute, conversation):
    if attribute == "model":
        print(ConversationManager.get_model(conversation))
    elif attribute == "conversation":
        print(ConversationManager.get_conversation_info(conversation))
    elif attribute == "temp":
        print(ConversationManager.get_temperature(conversation))
    else:
        print(f"Unknown attribute: {attribute}")

def system_update(attribute, value, conversation):
    if attribute == "model":
        ConversationManager.set_model(conversation, value)
    elif attribute == "temp":
        ConversationManager.set_temperature(conversation, value)
    else:
        print(f"Unknown attribute: {attribute}")

def system_show_model_info(attribute):
    if attribute == "available":
        print(ModelManager.get_available_models())
    elif attribute == "downloaded":
        print(ModelManager.get_downloaded_models())
    elif attribute == "running":
        print(ModelManager.get_running_models())

def system_install_model(attribute):
        utils.install_ollama_model(attribute)
        print(ModelManager.get_downloaded_models())

def system_uninstall_model(attribute):
        utils.uninstall_ollama_model(attribute)
        print(ModelManager.get_downloaded_models())

def system_help_command():
    print ("Overview of Possible Commands")
    for cmd_word in system_key_words:
        print(f"{cmd_word} - ", system_key_words[cmd_word]["description"])

def system_show_stats(attribute):
    if attribute == "cpu":
        print(f"CPU Usage: {RuntimeMonitor.get_cpu_usage()}%")

    elif attribute == "memory":
        mem = RuntimeMonitor.get_memory_usage()
        print(f"Memory: {mem['used']}/{mem['total']} ({mem['percent']}%)")

    elif attribute == "gpu":
        gpu = RuntimeMonitor.get_gpu_usage()
        if gpu is None:
            print("GPU usage not available")
        else:
            print(f"GPU Usage: {gpu:.2f}%")

    elif attribute == "vram":
        vram = RuntimeMonitor.get_vram_usage()
        if vram is None:
            print("VRAM usage not available")
        else:
            print(f"VRAM: {vram['used']}MB / {vram['total']}MB {vram['percent']:.2f}%")

    elif attribute == "all":
        cpu = RuntimeMonitor.get_cpu_usage()
        mem = RuntimeMonitor.get_memory_usage()
        gpu = RuntimeMonitor.get_gpu_usage()
        vram = RuntimeMonitor.get_vram_usage()
        print(f"CPU Usage: {cpu}%")
        print(f"Memory: {mem['used']}/{mem['total']} ({mem['percent']}%)")
        if gpu is None:
            print("GPU Usage: not available")
        else:
            print(f"GPU Usage: {gpu:.2f}%")
        if vram is None:
            print("VRAM Usage: not available")
        else:
            print(f"VRAM: {vram['used']}MB / {vram['total']}MB {vram['percent']:.2f}%")
    
    if attribute == "live":
        try:
            while True:
                subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
                print("=== LIVE SYSTEM STATS ===\n")
                system_show_stats("all")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nLive stats stopped.")
            return


def system_parserbuilder(cmdword):
    parser = argparse.ArgumentParser(prog = cmdword, add_help=False)
    parser.add_argument("-h", "--help", action="help", help="display this help message (program continues)")
    arg_definitions = system_key_words[cmdword]["args"]
    for arg_def in arg_definitions:
        names = arg_def["flags"]
        metadata = arg_def["options"]
        parser.add_argument(*names, **metadata)
    return parser

conversation_key_words = {
    "load": {
        "description": "Load a file into the conversation context",
        "args": [
            {"flags": ["path"], "options": {"help": "Path to the file to load"}}
        ],
        "handler": lambda args: load_file(args.conversation, args.path)
    },

    "load_dir": {
        "description": "Load a directory into the conversation context",
        "args": [
            {"flags": ["path"], "options": {"help": "Path to the directory to load"}}
        ],
        "handler": lambda args: load_directory(args.conversation, args.path)
    },

    "help": {
        "description": "Show a list of available conversation commands",
        "args": [],
        "handler": lambda args: conversation_help()
    },
}

def conversation_dispatch(cmd, conversation):
    args = shlex.split(cmd)
    if not args:
        print("No conversation command given")
        return

    keyword = args[0]
    tokens = args[1:]

    if keyword not in conversation_key_words:
        print(f"Unknown conversation command: {keyword}")
        return

    parser = conversation_parserbuilder(keyword)

    try:
        parsed = parser.parse_args(tokens)
        parsed.conversation = conversation
        conversation_key_words[keyword]["handler"](parsed)
    except SystemExit:
        # argparse already printed help or error
        pass


# ---- handlers ----

def load_file(conversation, path):
    try:
        ContextLoader.file_to_context(conversation, path)
        print(f"Loaded file into context: {path}")
    except Exception as e:
        print(f"Error loading file: {e}")


def load_directory(conversation, path):
    try:
        ContextLoader.directory_to_context(conversation, path)
        print(f"Loaded directory into context: {path}")
    except Exception as e:
        print(f"Error loading directory: {e}")


def conversation_help():
    print("Conversation commands:")
    for cmd_word, meta in conversation_key_words.items():
        print(f"  {cmd_word} - {meta['description']}")


# ---- parser builder ----

def conversation_parserbuilder(cmdword):
    parser = argparse.ArgumentParser(prog=cmdword, add_help=False)
    parser.add_argument("-h", "--help", action="help",
                        help="display this help message (program continues)")

    arg_definitions = conversation_key_words[cmdword]["args"]
    for arg_def in arg_definitions:
        names = arg_def["flags"]
        metadata = arg_def["options"]
        parser.add_argument(*names, **metadata)

    return parser
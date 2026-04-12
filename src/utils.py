"""
File: utils.py
Author: MORS
Date: 22 MAR 26

Description:
Utility functions for interacting with the Ollama environment and providing
generic helpers that do not belong to any subsystem. Includes helpers for
conversation ID generation and model installation/removal. Stateless and
model-agnostic.

Responsibilities:
    - Provide small, generic helper functions.
    - Generate unique conversation IDs.
    - Install and uninstall Ollama models.
    - Avoid model logic, conversation logic, or persona logic.

Not Responsible For:
    - Running models or generating responses.
    - Managing conversation state or settings.
    - Loading personas or context.
    - Querying system telemetry (RuntimeMonitor).
    - Dispatching commands or REPL behavior.

Public API Contract:

    Static Methods:
        - generate_conv_id()
            Inputs: none
            Outputs: str
            Notes: Generates a timestamp-based unique conversation ID.

        - install_ollama_model(model)
            Inputs: model name (str)
            Outputs: None or error string
            Notes: Installs a model via the Ollama CLI.

        - uninstall_ollama_model(model)
            Inputs: model name (str)
            Outputs: None or error string
            Notes: Uninstalls a model via the Ollama CLI.

    Instance Methods (placeholders):
        - list_installed_models()
        - get_model_info(model_name)
        - get_ollama_version()
        - ping_ollama()


"""

import subprocess
from datetime import datetime


class Utils:
    # Generate a conversation ID based on the time
    @staticmethod
    def generate_conv_id():
        now = datetime.now()
        conv_id = now.strftime("%Y%m%d_%H%M%S_") + str(now.microsecond).zfill(6)
        return conv_id

    # Return a list of installed Ollama models
    def list_installed_models(self):
        pass

    # Return model details to include its family (e.g., llama3, mistral), size, version, etc.
    def get_model_info(self, model_name):
        pass

    # Return the version of the Ollama currently running
    def get_ollama_version(self):
        pass

    # Perform a simple health check to confirm the Ollama local server is running
    def ping_ollama(self):
        pass

    @staticmethod
    def install_ollama_model(model):
        print("Installing ", model, " this may take a moment.")
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            
            process.stdout.close()
            process.wait()
            print("Installation complete.")

        except Exception as e:
            return(f"Error installing model: {e}")
        
    
    @staticmethod
    def uninstall_ollama_model(model):
        print("Uninstalling", model, "...")
        try:
            process = subprocess.Popen(
                ["ollama", "rm", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            process.stdout.close()
            process.wait()
            print("Uninstall complete.")

        except Exception as e:
            return f"Error uninstalling model: {e}"

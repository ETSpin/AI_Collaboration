"""
Class: Utils
Author: MORS
Date: 22 MAR 26

Description:
Here the utility functions for interacting with the Ollama environment - i.e., find out which models are installed which version is running, etc.
This will be useful from the start  for  development and debugging purposes

Usage:
TBD...
"""

class Utils:

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
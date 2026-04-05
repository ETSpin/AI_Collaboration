"""
Class: Utils
Author: MORS
Date: 22 MAR 26

Description:
Here the utility functions for interacting with the Ollama environment - i.e., find out which models are installed which version is running, etc.
This will be useful from the start  for  development and debugging purposes

Responsibilities:
- Small, generic helpers that do not belong to any subsystem
- No model logic
- No conversation logic

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

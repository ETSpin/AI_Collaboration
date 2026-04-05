"""
Class: ModelManager
Author: MORS
Date: 22 MAR 26

Description:
Provides a unified interface for querying, inspecting, and managing available,
downloaded, and running models. This class isolates all model-related operations
from AppController and dispatcher, preventing circular imports and ensuring a
clean separation of responsibilities.

Responsibilities:
    - Query the Ollama CLI for downloaded models.
    - Query the Ollama CLI for running models.
    - Retrieve the list of models available for download from the Ollama library.
    - Provide a stable API for any component needing model information.
    - Serve as the single source of truth for model metadata.

Not Responsible For:
    - Managing conversations or application state.
    - Dispatching commands or parsing user input.
    - Running model inference (delegated to ModelRunner).
    - GUI rendering or display logic.
    - File or context ingestion.

Public API Contract:

    Static Methods:

        get_downloaded_models()
            Inputs: none
            Outputs: str (CLI output or error message)
            Notes: wraps `ollama list` to show installed models

        get_available_models()
            Inputs: none
            Outputs: str (HTML or error message)
            Notes: fetches the Ollama library page

        get_running_models()
            Inputs: none
            Outputs: str (CLI output or error message)
            Notes: wraps `ollama ps` to show active model processes
"""

import subprocess
import urllib.request


class ModelManager():
#Return the downloaded models - this is spawned as a subprocess to get to the Ollama Cli
    @staticmethod
    def get_downloaded_models():
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True,check=True)
            return result.stdout
        
        except Exception as e:
            return(f"Error retrieving model list: {e}")
        
    #Return the models available to be downloaded
    @staticmethod
    def get_available_models():
        try:
            url = "https://ollama.com/library"
            with urllib.request.urlopen(url) as response: # Fetch raw bytes from the URL
                raw_bytes = response.read()

            html = raw_bytes.decode("utf-8", errors="replace") # Decode as UTF‑8 safely
            return html
           
        except Exception as e:
            return(f"Error retrieving model list: {e}")

    #Return the models available to be downloaded - this is spawned as a subprocess to get to the Ollama Cli
    @staticmethod
    def get_running_models():
        
        try:
            result = subprocess.run(["ollama", "ps"],capture_output=True,text=True,check=True)
            return result.stdout

        except Exception as e:
            return(f"Error retrieving model list: {e}")

"""
Class: ModelManager
Author: MORS
Date: 22 MAR 26

Description:
Static utility class responsible for manipulating model-related settings
inside a ConversationObject and querying system-level model information
(downloaded, running, and available models).

ModelManager does NOT store defaults, load personalities.json, or maintain
any internal state. All defaults are provided externally by ConversationManager.

Responsibilities:
    - Update model_settings inside a ConversationObject.
    - Validate model_settings values.
    - Provide granular setters for common model parameters.
    - Provide system-level model queries (downloaded, running, available).

Not Responsible For:
    - Loading personalities.json (ContextManager).
    - Selecting or switching models (ConversationManager).
    - Running model inference.
    - Managing context or messages.
    - Holding internal state or defaults.

Public API Contract:
    Static Methods (settings):
        set_temperature(conversation, value)
        set_top_p(conversation, value)
        set_top_k(conversation, value)
        set_num_ctx(conversation, value)
        set_repeat_penalty(conversation, value)
        validate_settings(conversation)
        warn_if_suboptimal(conversation) -> list[str]

    Static Methods (system queries):
        get_downloaded_models()
        get_available_models()
        get_running_models()
"""

import subprocess
import urllib.request


class ModelManager:
    # -------------------------
    # Model Settings Manipulation
    # -------------------------
    @staticmethod
    def set_temperature(conversation, value: float):
        if not (0 <= value <= 1.3):
            raise ValueError("[ModelManager] temperature must be between 0 and 1.3")
        conversation.model_settings["temperature"] = value

    @staticmethod
    def set_top_p(conversation, value: float):
        if not (0 <= value <= 1):
            raise ValueError("[ModelManager] top_p must be between 0 and 1")
        conversation.model_settings["top_p"] = value

    @staticmethod
    def set_top_k(conversation, value: int | None):
        if value is not None and value < 0:
            raise ValueError("[ModelManager] top_k must be >= 0 or None")
        conversation.model_settings["top_k"] = value

    @staticmethod
    def set_num_ctx(conversation, value: int):
        if value <= 0:
            raise ValueError("[ModelManager] num_ctx must be > 0")
        conversation.model_settings["num_ctx"] = value

    @staticmethod
    def set_repeat_penalty(conversation, value: float):
        if value <= 0:
            raise ValueError("[ModelManager] repeat_penalty must be > 0")
        conversation.model_settings["repeat_penalty"] = value

    # Validate model settings in the conversation - raise ValueError i fsomething is wrong
    @staticmethod
    def validate_settings(conversation):
        settings = conversation.model_settings
        required_keys = ["temperature", "top_p", "top_k", "num_ctx", "repeat_penalty"]

        for key in required_keys:
            if key not in settings:
                raise ValueError(f"[ModelManager] Missing a required setting: '{key}'")

        temperature = settings.get("temperature")
        if not(0 <= temperature <= 1.1):
            raise ValueError("[ModelManager] Invalid temperature (must be between 0 and 1)")

        top_p = settings.get("top_p")
        if not (0 <= top_p <= 1):
            raise ValueError("[ModelManager] Invalid top_p (must be between 0 and 1)")

        top_k = settings.get("top_k")
        if top_k is not None and top_k < 0:
            raise ValueError("[ModelManager] Invalid top_k (must be >= 0 or None)")

        num_ctx = settings.get("num_ctx")
        if num_ctx <= 0:
            raise ValueError("[ModelManager] Invalid num_ctx (must be > 0)")

        repeat_penalty = settings.get("repeat_penalty")
        if repeat_penalty <= 0:
            raise ValueError("[ModelManager] Invalid repeat_penalty (must be > 0)")

    # Provide a list of model warnings for model settings that are valid but likely to produce poor or unstable model behavior
    @staticmethod
    def warn_if_suboptimal(conversation):
        warnings = []
        settings = conversation.model_settings

        # Check for missing keys (soft warning)
        required_keys = ["temperature", "top_p", "top_k", "num_ctx", "repeat_penalty"]
        for key in required_keys:
            if key not in settings:
                warnings.append(f"[ModelManager] Setting '{key}' is missing; model behavior may be unpredictable")

        # num_ctx controls how much conversation history the model can see
        num_ctx = settings.get("num_ctx")
        if num_ctx < 128:
            warnings.append(" [ModelManager] num_ctx is extremely low; the model will lose context almost immediately")
        elif num_ctx < 512:
            warnings.append("[ModelManager] num_ctx is low; multi-turn reasoning may be impaired")

        # temperature controls randomness and creativity in the model's output
        temperature = settings.get("temperature")
        if temperature > 1.0:
            warnings.append("[ModelManager] temperature above 1.0 may cause unpredictable, incoherent or chaotic output")
        elif temperature < 0.1:
            warnings.append("[ModelManager] temperature below 0.1 may cause overly literal or repetitive responses")

        # top_p controls the number of samples provided for selection by restricting the model to only the most probable tokens whose cumulative probability adds up to top_p
        top_p = settings.get("top_p")
        if top_p < 0.2:
            warnings.append("[ModelManager] top_p below 0.2 may cause truncated or repetitive responses")

        # top_k controls how many candidate tokens are considered at each step
        top_k = settings.get("top_k")
        if top_k is not None and top_k < 10:
            warnings.append("[ModelManager] top_k below 10 may reduce output diversity.")

        # repeat_penalty discourages the model from repeating itself
        rp = settings.get("repeat_penalty", 1.1)
        if rp < 1.0:
            warnings.append("[ModelManager] repeat_penalty below 1.0 may cause the model to repeat itself.")
        elif rp > 2.0:
            warnings.append("[ModelManager] repeat_penalty above 2.0 may cause the model to avoid repeating necessary words.")

        return warnings

    # -------------------------
    # System-Level Model Queries
    # -------------------------
    # Return the downloaded models - this is spawned as a subprocess to get to the Ollama Cli
    @staticmethod
    def get_downloaded_models():
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            return result.stdout

        except Exception as e:
            return f"[ModelManager] Error retrieving model list: {e}"

    # Return the models available to be downloaded
    @staticmethod
    def get_available_models():
        try:
            url = "https://ollama.com/library"
            with urllib.request.urlopen(url) as response:  # Fetch raw bytes from the URL
                raw_bytes = response.read()

            html = raw_bytes.decode("utf-8", errors="replace")  # Decode as UTF‑8 safely
            return html

        except Exception as e:
            return f"[ModelManager] Error retrieving model list: {e}"

    # Return the models available to be downloaded - this is spawned as a subprocess to get to the Ollama Cli
    @staticmethod
    def get_running_models():
        try:
            result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
            return result.stdout

        except Exception as e:
            return f"[ModelManager] Error retrieving model list: {e}"

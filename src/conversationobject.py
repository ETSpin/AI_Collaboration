"""
File: conversationobject.py
Author: MORS
Date: 28 MAR 26

Description:
Represents a single conversational session between the user and an AI persona.
Stores all stateful information required to run, resume, serialize, or inspect a
conversation. Acts as a structured container for model configuration, message
history, metadata, and lifecycle timestamps. A ConversationObject holds the
three components required to execute a model turn:

    1. model_settings   (from ModelManager)
    2. context_components (from ContextManager)
    3. message_history  (from MessageManager)

It is immutable in structure but mutable in content (messages grow, metadata
updates, timestamps change). It does NOT run the model and does NOT modify
its own messages.

Responsibilities:
    - Store the model name used for this conversation.
    - Store the externally assigned conversation_id.
    - Hold context_components (prompt_prefix, personality, rules).
    - Hold model_settings (temperature, top_p, num_ctx, etc.).
    - Store the message history list (role/content dicts).
    - Track creation and update timestamps.
    - Store metadata, token counts, and optional conversation title.
    - Store the assistant's prompt_name.
    - Provide read-only accessors for conversation state.
    - Provide readable __str__ and __len__ helpers for debugging.

Not Responsible For:
    - Running the model (ConversationManager does that).
    - Adding or modifying messages (MessageManager does that).
    - Generating conversation IDs (AppController/Utils).
    - Managing GUI or CLI output.
    - Loading personas or building context (ContextManager).
    - Managing or validating model settings (ModelManager).

Public API Contract:

    Constructor:
        __init__(model_name, conversation_id=None, context_block=None,
                 persona_name=None, persona_dict=None, model_settings=None,
                 messages=None, context_components=None, prompt_name="AI agent:")

    Properties:
        model_name (get/set)
        model_settings (get/set)
        context_block (get/set)
        messages (get)
        conversation_id (get/set)
        prompt_name (get/set)
        created_at (get/set)
        updated_at (get/set)
        metadata (get/set)
        token_count (get/set)
        title (get/set)

    Special Methods:
        __len__() → number of message turns
        __str__() → human-readable summary

"""

from datetime import datetime, timezone


class ConversationObject:
    # Represents a fully assembled conversational state at a single point in time.
    def __init__(
        self, model_name, conversation_id=None, context_block=None, persona_name=None, persona_dict=None, model_settings=None, messages=None, context_components=None, streaming=False, prompt_name="AI agent:"
    ):
        # -----------------------
        # Model Info
        # -----------------------
        self._model_name = model_name
        self._model_settings = model_settings if model_settings is not None else {}
        self._tokens_model_max = 0
        self._prompt_name = prompt_name
        self._streaming_enabled = streaming

        # -----------------------
        # Identity / Meta Data
        # -----------------------
        self._conversation_id = conversation_id
        self._created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._updated_at = None
        self._metadata = {}
        self._title = None  # summary of the conversation

        # -----------------------
        # Context Info
        # -----------------------
        self._context_components = context_components or {}
        self._context_block = context_block
        self._persona_name = persona_name
        self._persona_dict = persona_dict

        # -----------------------
        # Message Info
        # -----------------------
        self._messages = messages if messages is not None else []

        # -----------------------
        # File Info (ad hoc files / file metadata)
        # -----------------------
        self._files = {}
        self._files_directory_summary = ""  # formatted tree summary

        # -----------------------
        # Embed Info (per-conversation embedding state)
        # -----------------------
        self._embed_location = f"./src/raw/{conversation_id}" # Path where embeddings for this conversation are stored (set lazily)
        self._embed_manifest = {}  # filename -> file_hash (SHA256) for change detection
        self._embed_files = []  # list of filenames currently embedded
        self._embed_index_path = None  # explicit path to the FAISS (or backend) index file
        self._embed_status = "not_built"  # one of: "not_built", "building", "ready", "error"
        self._embed_last_built_at = 0.0  # epoch timestamp of last successful build
        self._embed_chunk_size = 2048  # chunking parameters (persisted for determinism)
        self._embed_chunk_overlap = 256
        self._embed_backend = "faiss-cpu"  # backend identifier (e.g., "faiss-cpu")
        self._embed_stats = {}  # quick stats: total_files, total_chunks, index_bytes, etc.
        self._embed_lock_id = None  # lock token to avoid concurrent builds
        self._embed_index = None
        self._embed_chunks = []
        self._embed_metadata = []

    # -------------------------
    # Properties
    # -------------------------
    # -----------------------
    # Model Info
    # -----------------------
    @property
    def model_name(self):
        return self._model_name

    @model_name.setter
    def model_name(self, value):
        self._model_name = value

    @property
    def model_settings(self):
        return self._model_settings

    @model_settings.setter
    def model_settings(self, value):
        self._model_settings = value

    @property
    def tokens_model_max(self):
        return self._tokens_model_max

    @tokens_model_max.setter
    def tokens_model_max(self, value):
        self._tokens_model_max = value

    @property
    def prompt_name(self):
        return self._prompt_name

    @prompt_name.setter
    def prompt_name(self, value):
        self._prompt_name = value

    @property
    def streaming_enabled(self):
        return self._streaming_enabled

    # -----------------------
    # Identity / Meta Data
    # -----------------------
    @property
    def conversation_id(self):
        return self._conversation_id

    @conversation_id.setter
    def conversation_id(self, value):
        self._conversation_id = value

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = value

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        self._updated_at = value

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # -----------------------
    # Context Info
    # -----------------------
    @property
    def context_components(self):
        return self._context_components

    @context_components.setter
    def context_components(self, value):
        self._context_components = value

    @property
    def context_block(self):
        return self._context_block

    @context_block.setter
    def context_block(self, value):
        self._context_block = value

    @property
    def persona_name(self):
        return self._persona_name

    @persona_name.setter
    def persona_name(self, value):
        self._persona_name = value

    @property
    def persona_dict(self):
        return self._persona_dict

    @persona_dict.setter
    def persona_dict(self, value):
        self._persona_dict = value

    # -----------------------
    # Message Info
    # -----------------------
    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    # -----------------------
    # File Info
    # -----------------------
    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        self._files = value

    @property
    def files_directory_summary(self):
        return self._files_directory_summary

    @files_directory_summary.setter
    def files_directory_summary(self, value):
        self._files_directory_summary = value

    # -----------------------
    # Embed Info
    # -----------------------
    @property
    def embed_location(self):
        return self._embed_location

    @embed_location.setter
    def embed_location(self, value):
        self._embed_location = value

    @property
    def embed_manifest(self):
        return self._embed_manifest

    @embed_manifest.setter
    def embed_manifest(self, value):
        self._embed_manifest = value

    @property
    def embed_files(self):
        return self._embed_files

    @embed_files.setter
    def embed_files(self, value):
        self._embed_files = value

    @property
    def embed_index_path(self):
        return self._embed_index_path

    @embed_index_path.setter
    def embed_index_path(self, value):
        self._embed_index_path = value

    @property
    def embed_status(self):
        return self._embed_status

    @embed_status.setter
    def embed_status(self, value):
        self._embed_status = value

    @property
    def embed_last_built_at(self):
        return self._embed_last_built_at

    @embed_last_built_at.setter
    def embed_last_built_at(self, value):
        self._embed_last_built_at = value

    @property
    def embed_chunk_size(self):
        return self._embed_chunk_size

    @embed_chunk_size.setter
    def embed_chunk_size(self, value):
        self._embed_chunk_size = value

    @property
    def embed_chunk_overlap(self):
        return self._embed_chunk_overlap

    @embed_chunk_overlap.setter
    def embed_chunk_overlap(self, value):
        self._embed_chunk_overlap = value

    @property
    def embed_backend(self):
        return self._embed_backend

    @embed_backend.setter
    def embed_backend(self, value):
        self._embed_backend = value

    @property
    def embed_stats(self):
        return self._embed_stats

    @embed_stats.setter
    def embed_stats(self, value):
        self._embed_stats = value

    @property
    def embed_lock_id(self):
        return self._embed_lock_id

    @embed_lock_id.setter
    def embed_lock_id(self, value):
        self._embed_lock_id = value

    # -------------------------
    # Helpers
    # -------------------------
    # Returns the number of "turns" in the conversation
    def __len__(self):
        return len(self.messages)

    # Basic printout for a conversation object
    def __str__(self):
        lines = []
        lines.append(f"Conversation(model='{self._model_name}')")
        lines.append(f"  prompt_name: {self._prompt_name}")
        lines.append(f"  created_at: {self._created_at}")
        lines.append(f"  updated_at: {self._updated_at}")
        lines.append(f"  title: {self._title}")
        lines.append(f"  turns: {len(self._messages)}")
        lines.append("  messages:")

        for i, msg in enumerate(self._messages, start=1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            preview = content if isinstance(content, str) and len(content) <= 80 else (content[:77] + "..." if isinstance(content, str) else str(content))
            lines.append(f"    {i}. {role}: {preview}")
        return "\n".join(lines)

    def enable_streaming(self):
        self._streaming_enabled = True

    def disable_streaming(self):
        self._streaming_enabled = False

    # -----------------------
    # Embed Helpers
    # -----------------------

    # Return the manifest path under embed_location or None if not set
    def embed_manifest_path(self):
        if not self._embed_location:
            return None
        return f"{self._embed_location.rstrip('/')}/manifest.json"

    # Set embed_location (ConversationManager should ensure directory exists)
    def set_embed_location(self, path: str):
        self._embed_location = path

    # Update manifest and embed_files list (data-only)
    def update_embed_manifest(self, filename: str, file_hash: str):
        self._embed_manifest[filename] = file_hash
        if filename not in self.embed_files:
            self._embed_files.append(filename)

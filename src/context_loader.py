"""
File: context_loader.py
Author: MORS
Date: 3 APR 26

Description:
Allows the AI to inspect the filesystem for loading directories, reading files,
chunking or summarizing large content, and preparing structured context blocks
that can be injected into a Conversation object.

Responsibilities:
    - Inspect directories and return a structured tree.
    - Read file contents safely.
    - Chunk or summarize large files.
    - Provide context blocks formatted for LLM consumption.
    - Never modify conversation state directly.
    - Never call the model directly.

Not Responsible For:
    - Managing conversations or message history.
    - Calling or running any model.
    - GUI or CLI rendering.
    - Persona selection or context assembly logic.
    - Any form of model dispatch or routing.

Public API Contract:

    Static Methods:
        - list_directory(path)
            Inputs: path (str or Path)
            Outputs: list[dict]
            Notes: Returns directory entries with type and size.

        - read_file(path, max_bytes=None)
            Inputs: path, optional max_bytes
            Outputs: dict with path, content, size
            Notes: Safely reads file contents.

        - chunk_file(file_contents, max_chunk_size)
            Inputs: file_contents (str), max_chunk_size (int)
            Outputs: list[str]
            Notes: Splits large text into fixed-size chunks.

        - summarize_file(file_contents)
            Inputs: file_contents
            Outputs: summary or None
            Notes: Placeholder for future summarization.

        - build_context_block(path, contents)
            Inputs: path, contents
            Outputs: dict with formatted block
            Notes: Wraps file contents in LLM-readable structure.

        - file_to_context(conversation, path, max_chunk_size=8000)
            Inputs: conversation, path, max_chunk_size
            Outputs: bool
            Notes: Reads, chunks, formats, and injects file blocks.

        - directory_to_context(conversation, path, max_chunk_size=8000)
            Inputs: conversation, path, max_chunk_size
            Outputs: bool
            Notes: Loads all eligible files in a directory into context.

"""

from pathlib import Path

from message_manager import MessageManager


class ContextLoader:
    # Return a dict with the structure of the directory passed with by "path"
    @staticmethod
    def list_directory(path):
        dir_path = Path(path)
        results = []

        if not dir_path.exists() or not dir_path.is_dir():
            return []

        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    results.append({"type": "file", "name": item.name, "size": item.stat().st_size})
                else:
                    results.append({"type": "directory", "name": item.name, "size": None})
            return results

        except Exception as e:
            print(f"Error with path given: {e}")
            return []

    # Safely read a file's contents and return a dict with file information
    @staticmethod
    def read_file(path, max_bytes=None):
        file_path = Path(path)

        if not file_path.exists() or not file_path.is_file():
            return None

        try:
            file_size = file_path.stat().st_size
            if max_bytes is None or file_size <= max_bytes:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file_object:
                    file_content = file_object.read()
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file_object:
                    file_content = file_object.read(max_bytes)

            return {"path": str(file_path), "content": file_content, "size": file_size}

        except Exception as e:
            print(f"Error with file given: {e}")
            return None

    # Split a large file's contents into fixed-size chunks
    @staticmethod
    def chunk_file(file_contents, max_chunk_size):
        chunks = []
        index = 0

        if not file_contents:
            return []
        try:
            while index < len(file_contents):
                chunk = file_contents[index : index + max_chunk_size]
                chunks.append(chunk)
                index += max_chunk_size

            return chunks

        except Exception as e:
            print(f"Error chunking file: {e}")
            return []

    @staticmethod
    def summarize_file(file_contents):
        pass

    # Format the file's contents into a block readable by LLMs
    @staticmethod
    def build_context_block(path, contents):
        file_path = Path(path)

        if not file_path.exists() or not file_path.is_file() or not isinstance(contents, str) or not contents.strip():
            return None

        try:
            clean_text = contents.strip()
            context_block = f"=== FILE: {file_path} ===\n{clean_text}\n=== END FILE ==="

            return {"path": str(file_path), "contents": context_block}

        except Exception as e:
            print(f"Error building context block: {e}")
            return None

    #  Read a file, chunk it if necessary, format each chunk, and inject into the conversation as system messages
    @staticmethod
    def file_to_context(conversation, path, max_chunk_size=8000):
        file_path = Path(path)

        if not file_path.exists() or not file_path.is_file():
            print(f"Invalid file path: {file_path}")
            return False

        file_data = ContextLoader.read_file(file_path)
        if file_data is None:
            print(f"Could not read file: {file_path}")
            return False
        else:
            file_contents = file_data["content"]
            file_size = file_data["size"]

        try:
            if file_size <= max_chunk_size:
                block = ContextLoader.build_context_block(file_path, file_contents)
                if block:
                    system_msg = {"role": "system", "content": block["contents"]}
                    MessageManager.replace_system_message(conversation, system_msg)
                return True
            else:
                chunks = ContextLoader.chunk_file(file_contents, max_chunk_size)
                for chunk in chunks:
                    block = ContextLoader.build_context_block(file_path, chunk)
                    if block:
                        system_msg = {"role": "system", "content": block["contents"]}
                        MessageManager.replace_system_message(conversation, system_msg)
            return True

        except Exception as e:
            print(f"Error loading file into conversation {e}")
            return False

    #  Loading an entire directory structure into the context of a conversation
    @staticmethod
    def directory_to_context(conversation, path, max_chunk_size=8000):
        root = Path(path)

        if not root.exists() or not root.is_dir():
            print(f"Invalid directory: {root}")
            return False

        try:
            for file_path in root.rglob("*"):
                if file_path.is_file():
                    if file_path.suffix.lower() in {".py", ".txt", ".md"}:
                        ContextLoader.file_to_context(conversation, file_path.as_posix(), max_chunk_size)

            return True
        except Exception as e:
            print(f"Error converting directory structure into blocks {e}")
            return False

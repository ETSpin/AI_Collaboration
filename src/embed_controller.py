"""
Class: embed_controller.py
Author: MORS
Date: 20 APR 26

Description:
    Provides a stateless embedding pipeline for converting project files (.txt, .py, .pdf) into semantic vector representations using the
    nomic-embed-text model via Ollama (hard coded). Supports chunking, embedding,  FAISS index construction, and similarity search.

Responsibilities:
    - Read supported file types and extract text content
    - Chunk text into overlapping token windows
    - Generate embeddings for all chunks
    - Normalize and store vectors in a FAISS index
    - Perform semantic similarity search against the index
    - Produce metadata describing file, chunk index, token count, and page number
    - Provide hashing utilities for change detection

Not Responsible For:
    - Persisting embeddings or metadata to disk
    - Incremental rebuild logic or manifest management
    - File watching or directory monitoring
    - Error handling beyond minimal structural correctness
    - Application-level orchestration or UI integration

Public API Contract:

  Functions:
    build_index(file_paths, chunk_size=500, overlap=50, embed_model="nomic-embed-text")
        → Returns (faiss_index, chunks, metadata)

    search(query, index, chunks, metadata, top_k=5)
        → Returns ranked list of matching chunks with similarity scores

Static Methods:
    file_hash(text)
        → Hashes extracted text (legacy)

    file_hash_from_path(file_path)
        → Hashes raw file bytes for robust change detection

    embed_text(texts, model="nomic-embed-text", batch_size=16)
        → Embeds list of text chunks and returns float32 numpy array

    get_chunks_for_files(text, max_tokens=500, overlap=50)
        → Splits text into overlapping token chunks

    add_chunks(all_chunks, all_metadata, chunks, file_path, page=None)
        → Appends chunk text and metadata to master lists
"""

import hashlib
import os

import faiss
import numpy as np
import ollama as Ollama
import tiktoken
from PyPDF2 import PdfReader


class EmbedController:
    # Hashthe extracted text -- works for .txt files, not with .pdf or images
    @staticmethod
    def file_hash(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Better Hashing method - Hashes the raw file bytes, should work for all file types
    @staticmethod
    def file_hash_from_path(file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    # Build FAISS index with metadata
    @staticmethod
    def build_index(file_paths, chunk_size=500, overlap=50, embed_model="nomic-embed-text"):
        all_chunks = []
        all_metadata = []

        for file_path in file_paths:
            ext = os.path.splitext(file_path)[1].lower()

            if ext in (".txt", ".py"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                chunks = EmbedController.get_chunks_for_files(text, max_tokens=chunk_size, overlap=overlap)
                EmbedController.add_chunks(all_chunks, all_metadata, chunks, file_path)
            elif ext == ".pdf":
                pdfreader = PdfReader(file_path)
                for page_num, page in enumerate(pdfreader.pages):
                    text = page.extract_text() or ""
                    chunks = EmbedController.get_chunks_for_files(text, max_tokens=chunk_size, overlap=overlap)
                    EmbedController.add_chunks(all_chunks, all_metadata, chunks, file_path, page_num)
            else:
                print(f"⚠️ [EmbedController: ] Skipping unsupported file type: {file_path} ⚠️")

        vectors = EmbedController.embed_text(all_chunks)
        # Normalize for cosine similarity -- need to do more research on this concept
        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product = cosine similarity after normalization
        index.add(vectors)
        return index, all_chunks, all_metadata

    # Generate embeddings for a list of texts - uses the get_chunks_for_files() method
    @staticmethod
    def embed_text(texts, model="nomic-embed-text"):
        vectors = []
        for txt in texts:
            resp = Ollama.embeddings(model=model, prompt=txt)
            vectors.append(resp["embedding"])
        return np.array(vectors, dtype="float32")

    # Search the FAISS vector database for the most similar chunks - returns the text and metadata; Need to research this more
    @staticmethod
    def search(query, index, chunks, metadata, top_k=5):
        query_vec = EmbedController.embed_text([query])
        faiss.normalize_L2(query_vec)  # Normalize query for cosine similarity - need to research this more
        distances, indices = index.search(query_vec, top_k)
        results = []
        for rank, idx in enumerate(indices[0]):  # rank = the position in the top‑k list (0 = best match), idx = the index of the chunk in the chunks[] list
            if idx == -1:
                continue
            results.append(
                {
                    "text": chunks[idx],
                    "metadata": metadata[idx],
                    "similarity": float(distances[0][rank]),  # Cosine similarity score
                }
            )
        return results

    # Split text into overlapping token chunks
    @staticmethod
    def get_chunks_for_files(text, max_tokens=500, overlap=50):
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        chunks = []
        stride = max_tokens - overlap
        for i in range(0, len(tokens), stride):
            chunk_tokens = tokens[i : i + max_tokens]
            chunks.append(encoding.decode(chunk_tokens))
        return chunks

    # Helper Method for build_index to append chunks + metadata cleanly
    @staticmethod
    def add_chunks(all_chunks, all_metadata, chunks, file_path, page=None):
        filename = os.path.basename(file_path)

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            meta = {
                "file": filename,
                "chunk_index": i,
                "token_count": len(chunk),
            }
            if page is not None:
                meta["page"] = page
            all_metadata.append(meta)

    # Hashthe extracted text -- works for .txt files, not with .pdf or images
    @staticmethod
    def file_hash(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Placeholder for future incremental rebuild logic
    @staticmethod
    def file_needs_embedding(filename, file_hash):
        pass

    def invalidate_file(self, filename):
        pass

    def invalidate_all(self):
        pass

    def status(self):
        pass

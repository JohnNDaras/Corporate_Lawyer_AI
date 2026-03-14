from __future__ import annotations
from dataclasses import dataclass
from typing import List
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .types import Passage


@dataclass
class RAGConfig:
    index_path: str = "indices/faiss.index"
    metadata_path: str = "indices/faiss_meta.pkl"
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class FAISSRetriever:
    def __init__(self, cfg: RAGConfig):
        self.cfg = cfg
        self.model = SentenceTransformer(cfg.model_name)
        self.index = None
        self.metadata = []

        if os.path.exists(cfg.index_path):
            self.index = faiss.read_index(cfg.index_path)
            with open(cfg.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)

    def build_index(self, passages: List[Passage]):
        texts = [p.text for p in passages]
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        os.makedirs("indices", exist_ok=True)
        faiss.write_index(self.index, self.cfg.index_path)

        self.metadata = passages
        with open(self.cfg.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

        print(f"Indexed {len(passages)} passages into FAISS.")

    def retrieve(self, query: str, clause_label: str, k: int = 3) -> List[Passage]:
        if self.index is None:
            return []

        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                passage = self.metadata[idx]
                if passage.clause_type == clause_label:
                    results.append(passage)

        return results[:k]

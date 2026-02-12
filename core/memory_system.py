import numpy as np
import json
import os
import logging
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from config.settings import MEMORY_CONFIG

try:
    from core.chroma_store import ChromaStore
    HAS_CHROMA = True
except Exception:
    HAS_CHROMA = False

embedding_model = SentenceTransformer(MEMORY_CONFIG["embedding_model"])

class NumpyVectorDB:
    def __init__(self, filepath=MEMORY_CONFIG["memory_db_file"]):
        self.filepath = filepath
        self.texts = []
        self.vectors = None
        self.load()

    def add(self, text, vector):
        self.texts.append(text)
        vec_np = np.array([vector], dtype=np.float32)
        if self.vectors is None: self.vectors = vec_np
        else: self.vectors = np.vstack([self.vectors, vec_np])
        if len(self.texts) % 5 == 0: self.save()

    def search(self, query_vec, top_k=2, threshold=0.5):
        if self.vectors is None or len(self.texts) == 0: return []
        norm_vectors = np.linalg.norm(self.vectors, axis=1)
        norm_query = np.linalg.norm(query_vec)
        if norm_query == 0: return []
        similarities = np.dot(self.vectors, query_vec) / (norm_vectors * norm_query)
        indices = np.where(similarities > threshold)[0]
        sorted_indices = indices[np.argsort(similarities[indices])[::-1]]
        return [self.texts[i] for i in sorted_indices[:top_k]]

    def save(self):
        data = {"texts": self.texts, "vectors": self.vectors.tolist() if self.vectors is not None else []}
        with open(self.filepath, "w", encoding="utf-8") as f: json.dump(data, f)

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.texts = data.get("texts", [])
                    if data.get("vectors"): self.vectors = np.array(data["vectors"], dtype=np.float32)
            except Exception as e: logging.error(f"Memory load failed: {e}")

class ContextManager:
    def __init__(self, use_chroma=MEMORY_CONFIG["use_chroma"], chroma_persist_dir=MEMORY_CONFIG["chroma_persist_dir"]):
        self.buffer = []
        self.queue = []
        self.max_buffer = MEMORY_CONFIG["stm_buffer_size"]
        self._using = "numpy"
        self._init_db(use_chroma, chroma_persist_dir)
        self.stats = {"consolidated_count": 0, "retrieved_count": 0}

    def _init_db(self, use_chroma, chroma_persist_dir):
        if use_chroma and HAS_CHROMA:
            try:
                self.db = ChromaStore(persist_directory=chroma_persist_dir)
                self._using = "chroma"
                logging.info("[Memory] Using Chroma Vector DB")
                return
            except Exception as e: logging.warning(f"[Memory] Chroma failed: {e}")
        self.db = NumpyVectorDB()
        logging.info("[Memory] Using Numpy Vector DB")

    def add_to_buffer(self, role: str, content: str):
        self.buffer.append(f"{role}: {content}")
        if len(self.buffer) > self.max_buffer:
            self.queue.append(self.buffer.pop(0))

    def get_recent_context(self, num_turns: int = 5) -> str:
        return "\n".join(self.buffer[-num_turns:])

    async def process_queue(self, neural_engine):
        if not self.queue: return
        text = self.queue.pop(0)
        try:
            summary = await neural_engine.compress_text(text)
            vector = embedding_model.encode(summary).tolist()
            if self._using == "chroma": self.db.add_memory(summary, vector, source="consolidation")
            else: self.db.add(summary, vector)
            self.stats["consolidated_count"] += 1
            logging.info(f"[Memory/LTM] ✓ Consolidated: {summary[:60]}...")
        except Exception as e: logging.error(f"[Memory/LTM] Process failed: {e}")

    def retrieve_relevant(self, query_text: str, top_k: int = 4) -> List[str]:
        try:
            query_vec = embedding_model.encode(query_text).tolist()
            if self._using == "chroma":
                results = self.db.query(query_vec, top_k=top_k, threshold=MEMORY_CONFIG["retrieval_threshold"])
                docs = [r['document'] for r in results]
            else: docs = self.db.search(query_vec, top_k=top_k)
            self.stats["retrieved_count"] += len(docs)
            return docs
        except Exception as e:
            logging.error(f"[Memory/Retrieval] Failed: {e}")
            return []

    def get_memory_stats(self) -> dict:
        stats = {
            "backend": self._using,
            "buffer_size": len(self.buffer),
            "queue_size": len(self.queue),
            "consolidated": self.stats["consolidated_count"],
            "retrieved": self.stats["retrieved_count"]
        }
        if self._using == "chroma":
            try: stats["ltm_total"] = self.db.get_stats().get("total_documents", 0)
            except: pass
        return stats

class ProfileManager:
    def __init__(self, filepath=MEMORY_CONFIG["profile_file"]):
        self.filepath = filepath
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "name" not in data: data["name"] = "Nova"
                if "facts" not in data: data["facts"] = []
                return data
        return {"name": "Nova", "facts": []}

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f: json.dump(self.data, f)

    def update(self, key, value):
        self.data[key] = value
        self.save()
        
    def add_fact(self, fact):
        if fact not in self.data.get('facts', []):
            if 'facts' not in self.data: self.data['facts'] = []
            self.data['facts'].append(fact)
            self.save()

    def get_core_prompt(self):
        name, facts = self.data.get('name', 'Nova'), self.data.get('facts', [])
        facts_str = ', '.join(facts[-5:]) if facts else "none yet"
        return f"Your name is {name}. Known user facts: {facts_str}."

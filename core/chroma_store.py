import os
import logging
import time
import hashlib
from typing import List, Optional, Dict, Any
from config.settings import MEMORY_CONFIG

try:
    import chromadb
    from chromadb.config import Settings
except Exception as e:
    chromadb = None
    Settings = None
    logging.warning(f"chromadb not installed: {e}")

class ChromaStore:
    def __init__(self, persist_directory: str = MEMORY_CONFIG["chroma_persist_dir"], 
                 collection_name: str = MEMORY_CONFIG["chroma_collection"]):
        if chromadb is None:
            raise RuntimeError("chromadb is not installed.")
        os.makedirs(persist_directory, exist_ok=True)
        self.persist_dir = persist_directory
        try:
            self.client = chromadb.Client(Settings(persist_directory=persist_directory, is_persistent=True))
        except TypeError:
            self.client = chromadb.Client(Settings(persist_directory=persist_directory))
        
        self.collection_name = collection_name
        try:
            self.col = self.client.get_collection(name=collection_name)
            logging.info(f"[Chroma] Loaded collection: {collection_name}")
        except Exception:
            self.col = self.client.create_collection(
                name=collection_name,
                metadata={"description": "PKIC Agent Long-Term Memory"}
            )
            logging.info(f"[Chroma] Created collection: {collection_name}")

    def upsert(self, ids: List[str], documents: List[str], embeddings: List[List[float]], 
               metadatas: Optional[List[dict]] = None):
        try:
            self.col.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas or [{} for _ in documents]
            )
            logging.debug(f"[Chroma] Upserted {len(ids)} documents")
        except Exception as e:
            logging.error(f"[Chroma] Upsert failed: {e}")
            raise

    def add_memory(self, document: str, embedding: List[float], 
                   source: str = "consolidation", metadata: Optional[Dict[str, Any]] = None):
        if metadata is None: metadata = {}
        ts = time.time()
        doc_hash = hashlib.sha256((document + str(ts)).encode()).hexdigest()[:8]
        memory_id = f"mem_{source}_{doc_hash}_{int(ts)}"
        metadata.update({"timestamp": ts, "source": source, "length": len(document)})
        self.upsert([memory_id], [document], [embedding], [metadata])
        return memory_id

    def query(self, query_embedding: List[float], top_k: int = 4, 
              threshold: Optional[float] = None, where: Optional[dict] = None):
        try:
            res = self.col.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            p_ids = res.get("ids", [[]])[0]
            
            docs = []
            for doc_id, d, dist, m in zip(p_ids, p_docs, p_dists, p_meta):
                if threshold is None or dist <= threshold:
                    docs.append({"id": doc_id, "document": d, "distance": dist, "metadata": m})
            return docs
        except Exception as e:
            logging.error(f"[Chroma] Query failed: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        try:
            return {
                "collection": self.collection_name,
                "total_documents": self.col.count(),
                "persist_directory": self.persist_dir
            }
        except Exception as e:
            logging.error(f"[Chroma] Stats failed: {e}")
            return {}

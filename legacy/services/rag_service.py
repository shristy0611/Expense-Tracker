import os
import threading
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from flask import current_app
from models import Transaction

class RAGService:
    """Retrieval-Augmented Generation service using FAISS and sentence-transformers."""
    _lock = threading.Lock()
    _model = None
    _index = None
    _texts = []

    @classmethod
    def initialize(cls, app=None, index_path=None, texts_path=None):
        """Initialize FAISS index and load or build embeddings."""
        app = app or current_app
        with cls._lock:
            if cls._model is None:
                cls._model = SentenceTransformer(
                    app.config.get('RAG_MODEL_NAME', 'all-MiniLM-L6-v2')
                )
            index_path = index_path or app.config.get('RAG_INDEX_PATH', 'rag.index')
            texts_path = texts_path or app.config.get('RAG_TEXTS_PATH', 'rag_texts.npy')
            # Load existing index
            if os.path.exists(index_path) and os.path.exists(texts_path):
                cls._index = faiss.read_index(index_path)
                cls._texts = list(np.load(texts_path, allow_pickle=True))
            else:
                # Build index from past transactions
                from application import db
                with app.app_context():
                    transactions = Transaction.query.all()
                    cls._texts = [t.receipt_data or '' for t in transactions]
                    embeddings = cls._model.encode(
                        cls._texts, convert_to_numpy=True
                    )
                    d = embeddings.shape[1]
                    cls._index = faiss.IndexFlatL2(d)
                    cls._index.add(embeddings)
                    faiss.write_index(cls._index, index_path)
                    np.save(texts_path, np.array(cls._texts, dtype=object))

    @classmethod
    def retrieve(cls, query, k=5):
        """Retrieve top-k similar receipt texts for RAG context."""
        if cls._index is None:
            cls.initialize()
        emb = cls._model.encode([query], convert_to_numpy=True)
        D, I = cls._index.search(emb, k)
        return [cls._texts[i] for i in I[0] if i < len(cls._texts)]

# End of RAGService implementation

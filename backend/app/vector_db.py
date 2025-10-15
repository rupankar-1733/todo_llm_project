import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

class VectorDB:
    def __init__(self, model_name='all-MiniLM-L6-v2', index_file='faiss_index.pkl'):
        self.model = SentenceTransformer(model_name)
        self.index_file = index_file
        self.dimension = 384  # all-MiniLM-L6-v2 embedding size
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_to_task = {}  # Maps FAISS index position to task data
        
        # Load existing index if available
        self.load_index()
    
    def encode_text(self, text):
        """Convert text to vector embedding"""
        return self.model.encode([text])[0]
    
    def add_task(self, task_id, title, description):
        """Add task to vector database"""
        text = f"{title} {description}"
        embedding = self.encode_text(text)
        
        # Add to FAISS index
        self.index.add(np.array([embedding], dtype=np.float32))
        
        # Store task metadata
        position = self.index.ntotal - 1
        self.id_to_task[position] = {
            'task_id': task_id,
            'title': title,
            'description': description,
            'text': text
        }
        
        self.save_index()
    
    def search_tasks(self, query, k=5):
        """Search for similar tasks"""
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.encode_text(query)
        
        # Search FAISS index
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32), 
            min(k, self.index.ntotal)
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx in self.id_to_task:
                task_data = self.id_to_task[idx].copy()
                task_data['similarity_score'] = float(distances[0][i])
                results.append(task_data)
        
        return results
    
    def save_index(self):
        """Save FAISS index and metadata"""
        with open(self.index_file, 'wb') as f:
            pickle.dump({
                'index': faiss.serialize_index(self.index),
                'id_to_task': self.id_to_task
            }, f)
    
    def load_index(self):
        """Load FAISS index and metadata"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'rb') as f:
                data = pickle.load(f)
                self.index = faiss.deserialize_index(data['index'])
                self.id_to_task = data['id_to_task']

# Global vector database instance
vector_db = VectorDB()

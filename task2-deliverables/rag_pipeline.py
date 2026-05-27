# Saveena Boga - RAG Pipeline
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

chunks = [
    'RAG stands for Retrieval Augmented Generation.',
    'The RAG pipeline has three steps: Retrieval, Augmentation, and Generation.',
    'RAG fixes the problem of constantly changing policies by retrieving relevant information dynamically.',
    'Semantic search finds documents based on meaning rather than exact words.',
    'Embeddings convert text into mathematical vectors where similar meanings end up close together.',
    'The dot product measures similarity between vectors by multiplying and adding values.',
    'ChromaDB is a free vector database used to store and retrieve embeddings efficiently.',
    'Chunking splits documents into sections with overlap to preserve context.',
    'Vector databases use smart indexing like HNSW for fast retrieval.',
    'Embedding models convert text into vectors that represent meaning.'
]

print('Loading embedding model...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Embedding 10 chunks...')
embeddings = model.encode(chunks)
query = 'How do embeddings work?'
print(f'Query: {query}')
query_embedding = model.encode([query])
similarities = cosine_similarity(query_embedding, embeddings)[0]
import numpy as np
top2 = np.argsort(similarities)[::-1][:2]
print('Top 2 relevant chunks:')
for i in top2:
    print(f'- {chunks[i]}')

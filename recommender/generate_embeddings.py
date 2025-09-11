import os
import sys
import django
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'code_judge.settings')
django.setup()

from problem.models import Problem

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), 'embedding', 'problems.faiss')

def generate_and_save_embeddings():
    """
    Generates embeddings for all problems and saves them to the DB.
    Creates and saves a FAISS index for similarity search.
    """
    print("Loading sentence transformer model...")
    model = SentenceTransformer(MODEL_NAME)

    problems = list(Problem.objects.all())
    if not problems:
        print("No problems found in the database.")
        return

    print(f"Found {len(problems)} problems. Generating embeddings...")

    # Prepare texts for embedding
    texts_to_embed = [
        f"Title: {p.title}. Tags: {', '.join(p.tags_list)}. Difficulty: {p.difficulty}. Description: {p.description}"
        for p in problems
    ]

    # Generate embeddings in batches
    embeddings = model.encode(texts_to_embed, show_progress_bar=True, convert_to_numpy=True)

    print("Saving embeddings to the database...")
    for i, problem in enumerate(problems):
        problem.embedding = embeddings[i].tobytes()
        problem.save()

    print("Creating and saving FAISS index...")
    # Ensure the directory for the FAISS index exists
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    
    # Create a FAISS index
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(embeddings.astype('float32'))

    # Save the index to disk
    faiss.write_index(index, FAISS_INDEX_PATH)

    print(f"Successfully generated embeddings for {len(problems)} problems.")
    print(f"FAISS index saved to {FAISS_INDEX_PATH}")

if __name__ == "__main__":
    generate_and_save_embeddings()
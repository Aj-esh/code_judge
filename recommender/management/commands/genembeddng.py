# recommender/management/commands/generate_embeddings.py
import numpy as np
import os
import faiss
import json
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
from problem.models import Problem

# Define where to save the files
INDEX_PATH = "recommender/data/problem_embeddings.faiss"
MAPPING_PATH = "recommender/data/problem_id_map.json"

class Command(BaseCommand):
    help = 'Generates and saves sentence embeddings for all problems.'

    def handle(self, *args, **options):
        self.stdout.write("Loading SentenceTransformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2') # A good, fast model

        self.stdout.write("Fetching all problems from the database...")
        problems = list(Problem.objects.all())
        if not problems:
            self.stdout.write(self.style.WARNING("No problems found in the database."))
            return

        # Combine relevant text fields for a richer embedding
        problem_texts = [
            f"Title: {p.title} Description: {p.description}"
            for p in problems
        ]

        os.makedirs("recommender/data", exist_ok=True)

        self.stdout.write(f"Generating embeddings for {len(problems)} problems...")
        embeddings = model.encode(problem_texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        # Create and save the FAISS index
        d = embeddings.shape[1] # Vector dimension
        index = faiss.IndexFlatL2(d) # Using L2 distance
        index.add(embeddings)
        faiss.write_index(index, INDEX_PATH)
        self.stdout.write(self.style.SUCCESS(f"FAISS index saved to {INDEX_PATH}"))

        # Create and save the mapping from index position to problem ID
        id_map = {i: problems[i].id for i in range(len(problems))}
        with open(MAPPING_PATH, 'w') as f:
            json.dump(id_map, f)
        self.stdout.write(self.style.SUCCESS(f"Problem ID map saved to {MAPPING_PATH}"))
from typing import List, Dict 

import numpy as np
import faiss

np.random.seed(42)

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384 

problems = []

def get_similar_by_embedding(query_embedding: np.ndarray, faiss_index, topk: int = 50) -> List[int]:
    """
    Search FAISS index for topk most similar problems.
    Returns list of indices.
    """
    query = query_embedding.reshape(1, -1)

    # Search
    _, indices = faiss_index.search(query, topk)
    return indices[0].tolist()


def compute_tag_score(candidate_tags: List[str], reference_tags: List[str]) -> float:
    """
    Compute normalized tag overlap score.
    Example: candidate=['dp','graph'], reference=['dp','array','graph'] → 2/3 ≈ 0.67
    """
    if not reference_tags:
        return 0.0
    common_tags = set(candidate_tags) & set(reference_tags)
    return len(common_tags) / len(reference_tags)

# testing
score = compute_tag_score(['dp', 'graph'], ['dp', 'array', 'graph'])

def rerank_recommendations(
    last_solved_indices: List[int],
    difficulty_filter: str,
    problems: List[Dict],
    faiss_index,
    topk: int = 20
) -> List[Dict]:
    """
    Rerank problems using:
      40%: embedding similarity to last 2 solved
      60%: tag overlap with last 5 solved
    Only recommend problems matching difficulty_filter.
    """
    # Part A: Getting avg embedding of last 2 solved,
    if len(last_solved_indices) >= 2:
        last_2 = last_solved_indices[-2:]
    elif len(last_solved_indices) == 1:
        last_2 = last_solved_indices
    else:
        last_2 = []

    if last_2:
        avg_embedding = np.mean(
            [problems[i]['embedding'] for i in last_2],
            axis=0
        ).astype('float32')
        # Get 10 most similar by embedding
        candidate_indices = get_similar_by_embedding(avg_embedding, faiss_index, topk=10)
    else:
        # No history → use first 10 problems as candidates
        candidate_indices = list(range(min(10, len(problems))))

    # Part B: Collect tags from last 5 solved,
    last_5   = last_solved_indices[-5:] if len(last_solved_indices) >= 5 else last_solved_indices
    reference_tags = []
    for idx in last_5:
        reference_tags.extend(problems[idx]['tags'])

    # Part C: Scoring
    scored_candidates = []

    for idx in candidate_indices:
        prob = problems[idx]
        if prob['difficulty'] != difficulty_filter:
            continue  # skip =/= diffaclty

        # embedding similarity score - 40%
        if last_2:
            candidate_emb = prob['embedding']
            cos_sim = np.dot(candidate_emb, avg_embedding) / (
                np.linalg.norm(candidate_emb) * np.linalg.norm(avg_embedding) + 1e-6
            )
            similarity_score = max(0.0, min(1.0, cos_sim))  # \in [0,1]
        else:
            similarity_score = 0.5  # or neutral

        # Compute tag score - 60%
        tag_score = compute_tag_score(prob['tags'], reference_tags)

        # Combine
        score = 0.4 * similarity_score + 0.6 * tag_score

        scored_candidates.append({
            'pid': prob['id'],
            'index': idx,
            'score': score,
            'similarity_score': similarity_score,
            'tag_score': tag_score,
            'tags': prob['tags'],
            'difficulty': prob['difficulty']
        })

    # Sort by final score (descending)
    scored_candidates.sort(key=lambda x: x['score'], reverse=True)
    return scored_candidates[:topk]
from django.db.models import Q, Count
from django.db import models

from django.test import tag
from problem.models import Problem
from accounts.models import UserProfile

import os
import numpy as np
import faiss

from django.conf import settings
from recommender.recommendation import rerank_recommendations

FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, 'recommender', 'embedding', 'problems.faiss')

def load_recommendation(
        user, 
        difficulty,
        topk=10
    ):
    """
    Generates personalized problem recommendations for a user using reranking.
    """
    userprofile = UserProfile.objects.filter(user=user).first()
    print("user profile", userprofile)
    if not userprofile:
        return Problem.objects.none()
    
    all_problems = list(Problem.objects.all())
    problem_map = {
        p.id : p for p in all_problems
    }
    problem_list = []
    for i, p in enumerate(all_problems):
        embedding_bytes = p.embedding
        if embedding_bytes:
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            problem_list.append({
                'index': i,
                'id': p.id,
                'tags': p.tags_list,
                'difficulty': p.difficulty.lower(),
                'embedding': embedding
            })

    problemid_index = {
        p['id'] : p['index'] for p in problem_list
    }
    solved_pid = userprofile.last_5_solved_pids
    last_solved_indices = [problemid_index[pid] for pid in solved_pid if pid in problemid_index]

    try:
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    except RuntimeError:
        # Fallback if index is not found
        return tag_ranker(user)
    
    recommended_data = rerank_recommendations(
        last_solved_indices=last_solved_indices,
        difficulty_filter=difficulty.lower(),
        problems=problem_list,
        faiss_index=faiss_index,
        topk=topk
    )
    recommended_id = [data['pid'] for data in recommended_data]
    preserved_order = models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(recommended_id)])
    recommended_problems = Problem.objects.filter(id__in=recommended_id).order_by(preserved_order)
    return recommended_problems

def tag_ranker (user) :
    user_profile = UserProfile.objects.filter(user=user).first()
    
    
    user_tags = user_profile.tags.all()
    if not user_tags:
        return Problem.objects.none()
    _problem = _tag_ranker(user_tags)
    return _problem

def _tag_ranker (tags):
    """
    Rank problems based on tag match, difficulty, popularity, and recency.
    """
    if not tags:
        return Problem.objects.none()

    # Base queryset: Problems matching user's tags
    problems = Problem.objects.filter(tags__in=tags).distinct()

    problems = problems.annotate(
        tag_match_count=Count('tags', filter=Q(tags__in=tags)), 
        submission_count=Count('submissions'),
    ).order_by(
        '-tag_match_count', 
        'difficulty',       
        '-submission_count',
        '-created_at'       
    )
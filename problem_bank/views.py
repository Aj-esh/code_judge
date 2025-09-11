from django.shortcuts import render
from problem.models import Problem
from accounts.models import UserProfile
from .recommend import load_recommendation

from django.contrib.auth.decorators import login_required

from django.conf import settings
import os
import shutil
import random


# Create your views here.
def problem_bank(request):
    """
    Fetch relevent probblems and display the problem bank.
    """
    problems = None
    if request.user.is_authenticated:
        difficulty_filter = request.GET.get('difficulty', 'easy')
        problems = load_recommendation(
            user=request.user,
            difficulty=difficulty_filter,
            topk=20
        )
    
    # fallback logic
    if problems is None or not problems.exists():
        problems = list(Problem.objects.all())
        random.shuffle(problems)

    # delete tmp file
    # /code
    tmp_code_path = os.path.join(settings.BASE_DIR, 'compiler', 'tmp', 'code')
    shutil.rmtree(tmp_code_path)
    os.makedirs(tmp_code_path)

    # /executables
    tmp_exec_path = os.path.join(settings.BASE_DIR, 'compiler', 'tmp', 'executables')
    shutil.rmtree(tmp_exec_path)
    os.makedirs(tmp_exec_path)

    return render(request, 'problem_bank/problemset.html', {'problems': problems})
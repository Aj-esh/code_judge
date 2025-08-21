from pathlib import Path
from django.shortcuts import render
from problem.models import Problem
from django.contrib.auth.decorators import login_required
import random

from django.contrib.auth.decorators import login_required

from django.conf import settings
import os
import shutil
import random   

# Create your views here.
def _reset_tmp_dirs():
    """
    Safely reset compiler tmp directories (code, executables).
    Creates them if they do not exist; removes contents if they do.
    """
    base_tmp = Path(settings.BASE_DIR) / 'compiler' / 'tmp'
    code_dir = base_tmp / 'code'
    exec_dir = base_tmp / 'executables'

    for d in (code_dir, exec_dir):
        if d.exists():
            # Remove directory contents without failing if already gone (race-safe)
            shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)

def problem_bank(request):
    """
    Fetch relevent probblems and display the problem bank.
    """

    _reset_tmp_dirs()

    problems = list(Problem.objects.all())
    random.shuffle(problems)

    return render(request, 'problem_bank/problemset.html', {'problems': problems})
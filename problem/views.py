from django.shortcuts import render, redirect, get_object_or_404

import problem
from .models import Problem
from django.contrib.auth.decorators import login_required
from .forms import ProblemForm, SubmissionForm

import os
from django.conf import settings
from .ai_request import aicall
from .utils import (
    load_testcases,
    handle_submission,
    handle_run,
    handle_testcase
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .serializer import ProblemActionSerializer
from uuid import uuid4

# Create your views here.
@login_required
def p_detail(request, pid):
    """
    Fetch the problem details for a given problem ID and render the detail page.
    """
    problem = get_object_or_404(Problem, id=pid)
    form = SubmissionForm()
    chatspace_uuid = request.GET.get('cs', None)
    ctx = {'problem': problem, 'form': form, 'chatspace_uuid': chatspace_uuid}

    return render(request, 'problem/problem_detail.html', ctx)


class ProblemView(APIView):
    def post(self, request, pid):
        """
            Handle problem actions (submit, run, testcase) for pid problem
        """
        serializer = ProblemActionSerializer(data=request.data)

        if serializer.is_valid():
            action = serializer.validated_data['action']
            code = serializer.validated_data['code']
            language = serializer.validated_data['language']
            cinput = serializer.validated_data.get('cinput', '')

            try:
                problem = Problem.objects.get(id=pid)
            except Problem.DoesNotExist:
                return Response({"error": "Problem not found"}, status=status.HTTP_404_NOT_FOUND)

            testcases, error = load_testcases(pid)
            if error:
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

            if action == 'submit':
                result = handle_submission(code, language, testcases, problem)
            elif action == 'run':
                result = handle_run(code, language, testcases)
            elif action == 'testcase':
                result = handle_testcase(code, language, cinput)

            if result.get("cerror"):
                payload = [
                    problem.title,
                    problem.tags,
                    problem.constraints,
                    code,
                    result['cerror'],
                    result.get('status', "")
                ]
                result['ai_feedback'] = aicall(payload, action)                

            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@login_required
def create_chatspace_session(request):
    if request.method == 'POST':
        chatspace_uuid = str(uuid4())
        return Response({'chatspace_uuid': chatspace_uuid}, status=status.HTTP_200_OK)

    return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def create_problem(request):
    """
    Handle the creation of a new problem.
    """
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.creator = request.user
            problem.save()

            testcases = form.cleaned_data.get('testcases')

            testcase_file = os.path.join(settings.BASE_DIR, 'testcases', f'{problem.id}.json')

            with open(testcase_file, 'w') as f:
                f.write(testcases)

            return redirect('problem_detail', pid=problem.id)
        
    else:
        form =  ProblemForm()
    
    return render(request, 'problem/create_problem.html', {'form': form})


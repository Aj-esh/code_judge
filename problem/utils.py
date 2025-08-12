import os
import json

from django.conf import settings

from .validate import evaluate_submission, run


def load_testcases(pid):
    """
    Load test cases for a given pid.
    """
    testcase_file = os.path.join(settings.BASE_DIR, 'testcases', f'{pid}.json')
    try:
        with open(testcase_file, 'r') as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"{pid}; Test cases not found for this problem."
    except json.JSONDecodeError:
        return None, f"{pid}; Invalid test case format."


def handle_submission(code, language, testcases, pid, problem):
    """
    Handle the submission action.
    """
    evaluation_result = evaluate_submission(code, language, testcases, pid)
    problem.submissions += 1
    problem.save()
    return evaluation_result


def handle_run(code, language, testcases):
    """
    Handle the run action.
    """
    input_parts = []
    for value in testcases[0]['input'].values():
        if isinstance(value, list):
            input_parts.append(' '.join(map(str, value)))
        else:
            input_parts.append(str(value))
    cinput = '\n'.join(input_parts)
    return run(code, cinput, language)


def handle_testcase(code, language, cinput):
    """
    Handle the testcase action.
    """
    return run(code, cinput, language)
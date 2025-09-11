from compiler.views import execute

def run(code, cinput, language):
    """
    run, ctestcase, submit the code using a compiler app.

    """
    result = execute(language, code, cinput)
    return result

def validate_submission(coutput, expected_output):
    """
    Validate the output of a code submission against the expected output.
    Returns 
        True - output matches, 
        False - otherwise.
    """
    if isinstance(coutput, list):
        coutput = " ".join(map(str, coutput))
    coutput = coutput.strip().lower()

    if type(expected_output) == list:
        expected_output = " ".join(map(str, expected_output))
    expected_output = str(expected_output).strip().lower()

    if coutput == expected_output:
        return True
    return False

def evaluate_submission(code, language, testcases, pid):
    """
    Evaluates the user's code against a set of test cases.
    Returns a dictionary with the evaluation result.
    """
    for i, testcase in enumerate(testcases):
        try:
            # The input from the JSON file needs to be serialized back to a string
            # that the executed code can read from stdin.
            input_parts = []
            for key, value in testcase['input'].items():
                if isinstance(value, list):
                    input_parts.append(' '.join(map(str, value)))
                else:
                    input_parts.append(str(value))
            cinput = '\n'.join(input_parts)

            expected_output = testcase['output']

        except KeyError:
            return {
                'status': f"{pid}; Invalid test case format: 'input' or 'output' key missing in testcase {i+1}.",
                'cerror': "Invalid test case format."
            }

        result = run(code, cinput, language)
        coutput = result.get("coutput", "").strip().lower()
        cerr = result.get("cerror", "").strip()

        
        if cerr:
            return {
                'cerror': cerr + f" (Testcase {i+1}| {cinput} -> {expected_output} ~{coutput})",
                'status': f"{pid}; Error in testcase {i+1}: {cerr}"
            }
        
        if not validate_submission(coutput, expected_output):
            return {
                'cerror': f"Testcase {cinput} : {coutput}",
                'status': f"{pid}; Testcase {i+1} failed: expected '{expected_output}', got '{coutput}'"
            }
            
    return {'status': "Accepted!"}
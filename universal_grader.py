import subprocess
import os
import sys
import json

# Constants for evaluation
TIMEOUT = 2

def run_process(cmd, input_data):
    try:
        proc = subprocess.run(
            cmd, input=input_data, capture_output=True, text=True, timeout=TIMEOUT
        )
        return proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        return None, "Time Limit Exceeded", 124

def grade():
    # 1. Identify language and compile if necessary
    exec_cmd = []
    
    files = os.listdir(".")
    if "solution.py" in files:
        exec_cmd = ["python3", "solution.py"]
    elif "solution.c" in files:
        out, err, code = run_process(["gcc", "solution.c", "-o", "sol.out"], "")
        if code != 0:
            print(f"Compilation Error:\n{err}")
            print("STATUS:FAIL\nSCORE:0")
            return
        exec_cmd = ["./sol.out"]
    elif "solution.cpp" in files:
        out, err, code = run_process(["g++", "solution.cpp", "-o", "sol.out"], "")
        if code != 0:
            print(f"Compilation Error:\n{err}")
            print("STATUS:FAIL\nSCORE:0")
            return
        exec_cmd = ["./sol.out"]
    
    if not exec_cmd:
        print("Error: No solution file found")
        return

    # 2. Load JSON Test Cases
    if not os.path.exists("testcases.json"):
        print("Error: testcases.json missing")
        return
        
    with open("testcases.json", "r") as f:
        cases = json.load(f)
    
    passed = 0
    total = len(cases)
    
    for i, case in enumerate(cases):
        input_data = case.get("input", "")
        expected = case.get("output", "").strip()
        
        actual, err, code = run_process(exec_cmd, input_data)
        
        if actual == expected:
            passed += 1
        else:
            # FIX: Moved the replace outside the f-string to avoid SyntaxError
            safe_input = input_data.replace('\n', ' ')
            print(f"Test Case {i+1} Failed:")
            print(f"  Input: {safe_input}")
            print(f"  Expected: {expected}")
            print(f"  Got: {actual}")

    # 3. Final Result
    score = int((passed / total) * 100) if total > 0 else 0
    print(f"STATUS:{'PASS' if score == 100 else 'FAIL'}")
    print(f"SCORE:{score}")

if __name__ == "__main__":
    grade()

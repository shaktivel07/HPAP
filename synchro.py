#!/usr/bin/env python3
import os
import sys
import getpass
import json
import urllib.request
import subprocess

API_URL = "http://10.15.72.173:5005"

def api_call(endpoint, method="GET", data=None):
    url = f"{API_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, data=data) as f:
            return json.loads(f.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def list_questions():
    res = api_call("/api/list")
    if "error" in res:
        print(f"Error: {res['error']}")
        return
    print(f"\nAssessment: {res['assessment_id']}")
    print("-" * 45)
    for q in res['questions']:
        print(f"[{q['id']}] {q.get('title', q['id'])} ({q.get('difficulty', 'N/A')})")
    print("")

def show_question(qid):
    res = api_call(f"/api/show/{qid}")
    if "error" in res:
        print(f"Error: {res['error']}")
        return
    print(f"\n--- Question {qid} ---\n{res['task']}\n" + "-"*25)

def edit_solution(qid):
    sid = getpass.getuser()
    ext = "py" # Default, students can rename if they want
    sol_path = f"/home/{sid}/solutions/{qid}.{ext}"
    os.makedirs(os.path.dirname(sol_path), exist_ok=True)
    subprocess.run([os.environ.get('EDITOR', 'nano'), sol_path])

def evaluate(qid):
    sid = getpass.getuser()
    print(f"Submitting {qid} for evaluation...")
    res = api_call("/evaluate", "POST", {"student_id": sid, "question_id": qid})
    if "error" in res: print(f"Error: {res['error']}"); return
    print(f"\nStatus: {res['status']}\n" + "-"*20 + f"\nOutput:\n{res.get('output', 'N/A')}")

def ask_ai(query):
    print("🧠 AI is thinking (Llama 3)...")
    res = api_call("/api/ai/ask", "POST", {"query": query})
    if "response" in res:
        print("\n=== AI SUGGESTION ===")
        print(res["response"])
        print("=====================\n")
    else:
        print(f"Error: {res.get('error', 'AI is unavailable')}")

def main():
    if len(sys.argv) < 2:
        print("Usage: synchro <list|show|edit|eval|ai> [args]")
        return
    cmd = sys.argv[1]
    if cmd == "list": list_questions()
    elif cmd == "show" and len(sys.argv) == 3: show_question(sys.argv[2])
    elif cmd == "edit" and len(sys.argv) == 3: edit_solution(sys.argv[2])
    elif cmd == "eval" and len(sys.argv) == 3: evaluate(sys.argv[2])
    elif cmd == "ai" and len(sys.argv) >= 3: ask_ai(" ".join(sys.argv[2:]))
    else: print("Unknown command or missing arguments.")

if __name__ == "__main__":
    main()

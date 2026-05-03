import os
import json
import shutil
import subprocess
import tempfile
import resource
import logging
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_PATH = "/srv/assessment_system"
CORE_PATH = os.path.join(BASE_PATH, "core")
ASSESSMENTS_PATH = os.path.join(BASE_PATH, "assessments")
RUNTIME_BASE = os.path.join(CORE_PATH, "runtime")
ACTIVE_CONF = os.path.join(CORE_PATH, "active_assessment.conf")
SYSTEM_LOGS = os.path.join(BASE_PATH, "system_logs")
UNIVERSAL_GRADER = os.path.join(CORE_PATH, "universal_grader.py")

# RESOURCE LIMITS
LIMIT_CPU_SEC = 5
LIMIT_MEMORY_MB = 256
SANDBOX_USER = "sandbox_user"

os.makedirs(SYSTEM_LOGS, exist_ok=True)
# Ensure separate logger for Flask to avoid buffering issues
log_file = os.path.join(SYSTEM_LOGS, "backend.log")
logging.basicConfig(filename=log_file, level=logging.INFO)

def set_resource_limits():
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (LIMIT_CPU_SEC, LIMIT_CPU_SEC))
        mem_bytes = LIMIT_MEMORY_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_NPROC, (40, 40))
    except Exception as e:
        print(f"Error setting limits: {e}")

def get_active_config():
    if not os.path.exists(ACTIVE_CONF): return {"id": "", "ai_enabled": False}
    try:
        with open(ACTIVE_CONF, "r") as f: 
            data = f.read().strip()
            if not data: return {"id": "", "ai_enabled": False}
            return json.loads(data)
    except Exception as e: 
        logging.error(f"Config error: {e}")
        return {"id": "", "ai_enabled": False}

def ask_llama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3", "prompt": f"Helpful coding assistant. Concept: {prompt}", "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.json().get("response", "AI is unavailable.")
    except: return "Ollama is not responding."

# --- ADMIN UI v5 ---
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Teacher Admin Panel v5</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f0f2f5; color: #1c1e21; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 25px; }
        h2 { color: #007bff; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        button { background: #28a745; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        button:hover { background: #218838; }
        .tc-row { display: flex; gap: 10px; background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #007bff; }
        .tc-col { flex: 1; }
        .tc-col label { font-size: 11px; font-weight: bold; color: #007bff; }
        .tc-col textarea { height: 60px; margin-top: 4px; }
        .btn-add { background: #007bff; margin-bottom: 15px; }
        .btn-del { background: #dc3545; height: 40px; align-self: center; padding: 0 15px; }
        .ai-toggle { background: #6f42c1; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>👨‍🏫 Teacher Assessment Panel</h1>
    
    <div class="card">
        <h2>1. Assessment Control</h2>
        <input type="text" id="asm_id" placeholder="Assessment ID (e.g. lab_01)">
        <div class="ai-toggle">
            <input type="checkbox" id="ai_enable"> Enable AI Assistance (Llama 3)
        </div>
        <button onclick="createAsm()">1. Create Folder</button>
        <button onclick="activate()" style="background:#007bff">2. Publish Exam</button>
    </div>

    <div class="card">
        <h2>2. Add Question</h2>
        <div style="display:flex; gap:10px;">
            <input type="text" id="q_asm_id" placeholder="Assessment ID">
            <input type="text" id="q_id" placeholder="Question ID (e.g. 1.1)">
        </div>
        <input type="text" id="q_title" placeholder="Question Title">
        <input type="text" id="q_diff" placeholder="Difficulty (Easy/Medium/Hard)">
        <textarea id="q_task" rows="3" placeholder="Problem Statement..."></textarea>
        
        <label><strong>Test Cases:</strong></label>
        <div id="testcases_container">
            <!-- Dynamic pairs will appear here -->
        </div>
        <button class="btn-add" onclick="addTestCase()">+ Add New Test Case</button>
        <br>
        <button onclick="saveQuestion()">Save Question & All Test Cases</button>
    </div>

    <div class="card">
        <h2>3. Register Student</h2>
        <div style="display:flex; gap:10px;">
            <input type="text" id="stu_roll" placeholder="Roll Number">
            <input type="password" id="stu_pass" placeholder="Password">
        </div>
        <button onclick="addStu()">Register Student</button>
    </div>

    <script>
        let tcCount = 0;
        function addTestCase(inp="", out="") {
            tcCount++;
            const container = document.getElementById('testcases_container');
            const div = document.createElement('div');
            div.className = 'tc-row';
            div.id = 'tc_row_' + tcCount;
            div.innerHTML = `
                <div class="tc-col"><label>INPUT</label><textarea class="tc-input">${inp}</textarea></div>
                <div class="tc-col"><label>EXPECTED OUTPUT</label><textarea class="tc-output">${out}</textarea></div>
                <button class="btn-del" onclick="document.getElementById('tc_row_${tcCount}').remove()">X</button>
            `;
            container.appendChild(div);
        }

        async function apiPost(url, data) {
            const res = await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
            const result = await res.json();
            alert(result.message || result.status);
        }

        function createAsm() { apiPost('/api/admin/create_assessment', {id: document.getElementById('asm_id').value}); }
        function activate() { apiPost('/api/admin/activate', {id: document.getElementById('asm_id').value, ai_enabled: document.getElementById('ai_enable').checked}); }
        function addStu() { apiPost('/api/admin/add_student', {roll: document.getElementById('stu_roll').value, password: document.getElementById('stu_pass').value}); }

        function saveQuestion() {
            const rows = document.querySelectorAll('.tc-row');
            const testcases = [];
            rows.forEach(row => {
                testcases.push({
                    input: row.querySelector('.tc-input').value,
                    output: row.querySelector('.tc-output').value
                });
            });

            apiPost('/api/admin/add_question', {
                assessment_id: document.getElementById('q_asm_id').value,
                q_id: document.getElementById('q_id').value,
                title: document.getElementById('q_title').value,
                difficulty: document.getElementById('q_diff').value,
                task: document.getElementById('q_task').value,
                testcases: testcases
            });
        }

        addTestCase();
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---

@app.route("/admin")
def admin_panel(): return render_template_string(ADMIN_HTML)

@app.route("/api/admin/create_assessment", methods=["POST"])
def create_assessment():
    aid = request.json.get("id")
    os.makedirs(os.path.join(ASSESSMENTS_PATH, aid), exist_ok=True)
    return jsonify({"status": "success", "message": f"Assessment {aid} folder created."})

@app.route("/api/admin/add_question", methods=["POST"])
def add_question():
    data = request.json
    aid, qid = data.get("assessment_id"), data.get("q_id")
    q_path = os.path.join(ASSESSMENTS_PATH, aid, qid)
    os.makedirs(q_path, exist_ok=True)
    
    with open(os.path.join(q_path, "info.conf"), "w") as f:
        f.write(f"title:{data.get('title')}\ndifficulty:{data.get('difficulty')}")
    with open(os.path.join(q_path, "task.txt"), "w") as f:
        f.write(data.get("task"))
    with open(os.path.join(q_path, "testcases.json"), "w") as f:
        json.dump(data.get("testcases"), f)
        
    return jsonify({"status": "success", "message": f"Question {qid} saved."})

@app.route("/api/admin/activate", methods=["POST"])
def activate_assessment():
    data = request.json
    config = {"id": data.get("id"), "ai_enabled": data.get("ai_enabled", False)}
    with open(ACTIVE_CONF, "w") as f: json.dump(config, f)
    return jsonify({"status": "success", "message": "Exam published."})

@app.route("/api/admin/add_student", methods=["POST"])
def add_student():
    roll, password = request.json.get("roll"), request.json.get("password")
    try:
        subprocess.run(["useradd", "-m", "-s", "/bin/bash", roll], check=False)
        subprocess.run(["sh", "-c", f"echo '{roll}:{password}' | chpasswd"], check=True)
        os.makedirs(f"/home/{roll}/solutions", exist_ok=True)
        os.makedirs(f"/home/{roll}/logs", exist_ok=True)
        subprocess.run(["chown", "-R", f"{roll}:{roll}", f"/home/{roll}"], check=True)
        subprocess.run(["chmod", "700", f"/home/{roll}"], check=True)
        return jsonify({"status": "success", "message": f"Student {roll} registered."})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/list")
def list_questions():
    config = get_active_config()
    aid = config.get("id")
    if not aid: return jsonify({"error": "No active assessment"}), 404
    a_path = os.path.join(ASSESSMENTS_PATH, aid)
    questions = []
    if os.path.exists(a_path):
        for qid in sorted(os.listdir(a_path)):
            q_dir = os.path.join(a_path, qid)
            if os.path.isdir(q_dir):
                title, diff = qid, "N/A"
                if os.path.exists(os.path.join(q_dir, "info.conf")):
                    with open(os.path.join(q_dir, "info.conf"), "r") as f:
                        for line in f:
                            if "title:" in line: title = line.split(":", 1)[1].strip()
                            if "difficulty:" in line: diff = line.split(":", 1)[1].strip()
                questions.append({"id": qid, "title": title, "difficulty": diff})
    return jsonify({"assessment_id": aid, "questions": questions})

@app.route("/api/show/<qid>")
def show_question(qid):
    aid = get_active_config().get("id")
    task_path = os.path.join(ASSESSMENTS_PATH, aid, qid, "task.txt")
    if not os.path.exists(task_path): return jsonify({"error": "Not found"}), 404
    with open(task_path, "r") as f: return jsonify({"task": f.read()})

@app.route("/api/ai/ask", methods=["POST"])
def ai_assistant():
    config = get_active_config()
    if not config.get("ai_enabled"): return jsonify({"response": "AI assistance is not enabled."})
    return jsonify({"response": ask_llama(request.json.get("query"))})

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    sid, qid = data.get("student_id"), data.get("question_id")
    aid = get_active_config().get("id")
    run_dir = tempfile.mkdtemp(dir=RUNTIME_BASE)
    os.chmod(run_dir, 0o755)
    try:
        shutil.copy(UNIVERSAL_GRADER, os.path.join(run_dir, "grader.py"))
        shutil.copy(os.path.join(ASSESSMENTS_PATH, aid, qid, "testcases.json"), os.path.join(run_dir, "testcases.json"))
        found = False
        for ext in ["py", "c", "cpp"]:
            sol_path = os.path.join(f"/home/{sid}/solutions", f"{qid}.{ext}")
            if os.path.exists(sol_path):
                shutil.copy(sol_path, os.path.join(run_dir, f"solution.{ext}")); found = True; break
        if not found: return jsonify({"status": "FAIL", "output": "No solution file found"})
        for f in os.listdir(run_dir): os.chmod(os.path.join(run_dir, f), 0o644)
        result = subprocess.run(["sudo", "-u", SANDBOX_USER, "python3", "grader.py"], cwd=run_dir, capture_output=True, text=True, timeout=LIMIT_CPU_SEC + 10, preexec_fn=set_resource_limits)
        output = result.stdout + result.stderr
        status = "PASS" if "STATUS:PASS" in output else "FAIL"
        return jsonify({"status": status, "output": output})
    finally: shutil.rmtree(run_dir)

@app.route("/")
def home(): return "Backend live. Go to /admin"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)

# 📕 System Manual & Installation Guide

## ⚙️ 1. Technical Installation (Root Access Required)

### Prerequisites
*   **OS**: Linux (RHEL 9 / CentOS / Ubuntu)
*   **Compilers**: `gcc`, `gcc-c++`, `python3`
*   **Web Framework**: `Flask` (`pip install flask requests`)
*   **AI Engine**: [Ollama](https://ollama.com) with `llama3` model pulled.

### Steps:
1.  **Clone & Directory Setup**:
    ```bash
    mkdir -p /srv/assessment_system/{core,assessments,system_logs}
    mkdir -p /srv/assessment_system/core/runtime
    ```
2.  **User Provisioning**:
    ```bash
    useradd -r -s /usr/sbin/nologin sandbox_user
    chown -R root:root /srv/assessment_system
    chmod 711 /srv/assessment_system/core/runtime
    ```
3.  **Deploy Grader & CLI**:
    *   Place `universal_grader.py` into `/srv/assessment_system/core/`.
    *   Copy `synchro.py` to `/usr/local/bin/synchro` and `chmod +x /usr/local/bin/synchro`.
4.  **Start Services**:
    ```bash
    # Start Backend (Listening on 0.0.0.0:5005)
    nohup python3 backend_server.py > system_logs/flask.out 2>&1 & disown
    ```

---

## 👨‍🏫 2. Teacher User Manual

### Method A: Web Dashboard (Recommended)
1.  Navigate to `http://10.15.72.173:5005/admin`.
2.  **Create Assessment**: Enter a unique ID (e.g. `midterm_1`) to initialize a new exam.
3.  **Manage Questions**:
    *   Add Title and Difficulty.
    *   Test Cases: Click **"+ Add New Test Case"**. Enter the input (e.g. `5`) and expected output (`25`).
4.  **Student Management**: Enter the student's Roll Number and a custom Password to create their Linux account.
5.  **Publish**: Check the **"Enable AI"** box to allow students to use Llama 3 assistance.

### Method B: CLI Administration
Teachers can manually stage questions in:
`/srv/assessment_system/assessments/<ID>/<QID>/`
*   Create `task.txt` (Problem Description).
*   Create `testcases.json` (Array of `{"input": "...", "output": "..."}`).

---

## 🎓 3. Student User Manual (PowerShell)

1.  **Log In**:
    ```powershell
    ssh <ROLL_NUMBER>@10.15.72.173
    ```
2.  **View Work**:
    *   `synchro list`: See active questions and metadata.
    *   `synchro show 1.1`: Read the problem statement.
3.  **Code & Grade**:
    *   `synchro edit 1.1`: Opens the solution in `nano`. Save with `Ctrl+O`.
    *   `synchro eval 1.1`: Submit your code for sandboxed grading.
4.  **AI Assistant**:
    *   `synchro ai "Explain how a for loop works in C++"`
    *   *Note: This command will only respond if the teacher has enabled assistance for the specific test ID.*

# 🎓 Student Examination Manual

This manual provides the essential instructions for students to log in, write code, and submit their solutions on the HPAP platform.

---

## 1. Remote Access (Login)
The platform is hosted on a secure Linux server. You must connect via **SSH** using Windows PowerShell or a Terminal.

### Connecting via PowerShell:
1.  Open PowerShell.
2.  Type the following command (Replace `<ROLL>` with your ID):
    ```powershell
    ssh <ROLL>@10.15.72.173
    ```
3.  Enter your **Password** provided by the faculty. (Note: The password will be invisible as you type).

---

## 2. Navigating the Exam (`synchro`)
The `synchro` CLI is your primary tool for the exam. You do not need to change directories.

### 📋 List Questions
To see all questions in the current live exam:
```bash
synchro list
```

### 📖 View a Question
To read the instructions for a specific question (e.g., question 1.1):
```bash
synchro show 1.1
```

---

## 3. Solving the Problems

### 💻 Editing Your Code
To write or edit your code, use the `edit` command. This opens the **Nano** editor.
```bash
synchro edit 1.1
```
*   **Nano Shortcuts**:
    *   `Ctrl + O`, then `Enter`: Save your progress.
    *   `Ctrl + X`: Exit the editor.
*   **Language Selection**: 
    *   By default, the system creates a `.py` file. 
    *   If you prefer C, use `nano ~/solutions/1.1.c`.
    *   If you prefer C++, use `nano ~/solutions/1.1.cpp`.

### 🚀 Submission & Grading
To grade your code against the hidden test cases:
```bash
synchro eval 1.1
```
*   The system will compile (if C/C++) and run your code in a secure sandbox.
*   The output will show your **Pass/Fail** status and your **Score**.

---

## 🧠 4. AI Concepts Assistant
If enabled by your teacher, you can use the **Llama 3** assistant for help with coding concepts.
*   **Usage**:
    ```bash
    synchro ai "Explain how to implement a linked list in C"
    ```
*   **Restriction**: The AI is programmed to explain concepts and provide logic snippets, but it will not solve the exam question for you directly. 
*   **Note**: If the teacher has disabled the AI for this exam, you will receive a "Not Enabled" message.

---

## 📂 5. Your History
You can view your submission history and scores at any time by viewing your logs:
```bash
cat ~/logs/submissions.log
```

---

## ⚠️ Important Guidelines
1.  **Time Limits**: Each evaluation has a 2-second timeout. If your code is inefficient or has an infinite loop, it will fail automatically.
2.  **Resource Limits**: Your code is restricted to 256MB of RAM.
3.  **Submission Count**: You can evaluate as many times as you like. Only your **latest** score will be considered.
4.  **Network**: Do not attempt to use `curl`, `wget`, or any networking commands inside your code; the sandbox will block them.

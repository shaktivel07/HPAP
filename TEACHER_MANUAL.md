# 👨‍🏫 Teacher Administration Manual

This manual guides faculty through the complete lifecycle of managing exams, questions, and students using the HPAP platform.

---

## 1. Accessing the Control Panel
The primary interface for faculty is the web-based **Teacher Assessment Panel**.
*   **URL**: `http://<SERVER_IP>:5005/admin`
*   **Support**: For large-scale batch operations, see the **CLI Administration** section below.

---

## 2. Examination Lifecycle

### Step 1: Initializing an Assessment
1.  Navigate to the **Assessment Control** card.
2.  Enter a unique **Assessment ID** (e.g., `python_basic_101`).
3.  Click **Create Folder**. This initializes the storage namespace on the server.

### Step 2: Staging Questions
1.  Go to the **Add Question** section.
2.  **Target Assessment ID**: Must match the ID created in Step 1.
3.  **Question ID**: Numerical ID (e.g., `1.1`).
4.  **Metadata**: Provide a descriptive Title and Difficulty level.
5.  **Task**: Enter the instructions exactly as you want the student to see them.
6.  **Test Cases**:
    *   Click **+ Add New Test Case**.
    *   **Input**: Provide the exact input data (e.g., `5`).
    *   **Expected Output**: Provide the exact expected string (e.g., `25`).
    *   *Note: For array inputs, you can provide space-separated numbers in the Input box.*

### Step 3: Registering Students
1.  Go to the **Register Student** card.
2.  **Roll Number**: Use the official university ID.
3.  **Password**: Set a strong initial password.
4.  Click **Register**.
5.  *Security*: This creates a real, isolated Linux user account on the system.

### Step 4: Going Live (Publishing)
The exam is invisible to students until published.
1.  Enter the Assessment ID in the **Activate Exam** field.
2.  **AI Toggle**: Enable the checkbox if you want to allow students to use the **Llama 3** assistant for conceptual help.
3.  Click **Publish**.

---

## 3. CLI Administration (Power Users)
Teachers with server access can perform advanced batch operations using standard Linux tools.

### 3.1 Batch Student Registration
If you have a list of roll numbers in a text file (`rolls.txt`), use this bash snippet:
```bash
while read roll; do
    curl -X POST http://localhost:5005/api/admin/add_student \
         -H "Content-Type: application/json" \
         -d "{\"roll\":\"$roll\", \"password\":\"exam_pwd_2024\"}"
done < rolls.txt
```

### 3.2 Result Collection
After the exam, scores are stored in individual student home directories. To generate a consolidated report:
```bash
# Aggregates all submission logs into a single CSV
echo "Roll,Question,Status,Score" > results.csv
for log in /home/*/logs/submissions.log; do
    roll=$(echo $log | cut -d'/' -f3)
    awk -v r="$roll" '{print r "," $0}' "$log" >> results.csv
done
```

---

## 💡 Best Practices for Test Cases
*   **Precision**: Ensure there is no trailing whitespace in your "Expected Output" boxes.
*   **Diversity**: Add at least one "Edge Case" (e.g., negative numbers, empty arrays) to ensure code robustness.
*   **AI Guardrails**: Use the AI toggle wisely. It is recommended to keep it OFF for the first 30 minutes of a high-stakes exam.

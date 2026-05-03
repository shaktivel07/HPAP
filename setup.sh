#!/bin/bash

# Configuration
ROOT_DIR="/srv/assessment_system"

echo "=== Initializing Hardened SSH-Based Assessment Platform ==="

# 1. Core Directory Setup
mkdir -p "$ROOT_DIR/core/runtime"
mkdir -p "$ROOT_DIR/assessments"
mkdir -p "$ROOT_DIR/system_logs"
touch "$ROOT_DIR/core/active_assessment.conf"

# 2. Create Sandbox User (No shell, no home, low privilege)
if ! id "sandbox_user" &>/dev/null; then
    useradd -r -s /usr/sbin/nologin sandbox_user
    echo "Created sandbox_user."
fi

# 3. Permissions
chown -R root:root "$ROOT_DIR/assessments"
chmod -R 700 "$ROOT_DIR/assessments"
# Runtime needs to be accessible but the temp folders will be restricted
chmod 711 "$ROOT_DIR/core/runtime" 
chmod 755 "$ROOT_DIR/system_logs"

# 4. Install CLI Tool
cp synchro.py /usr/local/bin/synchro
chmod +x /usr/local/bin/synchro

# 5. Create Example Assessment
AID="hardened_assignment_1"
APATH="$ROOT_DIR/assessments/$AID"
mkdir -p "$APATH"

# Question 1.1: Hello Logic
QID="1.1"
QPATH="$APATH/$QID"
mkdir -p "$QPATH"
echo "Print 'Ready'" > "$QPATH/task.txt"
echo "title:Hello Ready\ndifficulty:Easy" > "$QPATH/info.conf"

# HARDENED GRADER: Runs solution as a SUBPROCESS (Issue #6)
cat <<EOF > "$QPATH/grader.py"
import subprocess
import sys

def run_solution():
    try:
        # Run student code as a separate process
        res = subprocess.run(
            ["python3", "solution.py"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if res.stdout.strip() == "Ready":
            print("STATUS:PASS\nSCORE:100")
        else:
            print(f"STATUS:FAIL\nExpected 'Ready', got '{res.stdout.strip()}'")
    except subprocess.TimeoutExpired:
        print("STATUS:FAIL\nERROR: Grader-side Timeout")
    except Exception as e:
        print(f"STATUS:FAIL\nERROR: {e}")

if __name__ == "__main__":
    run_solution()
EOF

chmod 600 "$APATH"/*/grader.py
chmod 644 "$APATH"/*/task.txt

# 6. Activate Assessment
echo "$AID" > "$ROOT_DIR/core/active_assessment.conf"

# 7. Student Creation Helper
create_student() {
    ROLL=$1
    if ! id "$ROLL" &>/dev/null; then
        useradd -m -s /bin/bash "$ROLL"
        echo "$ROLL:password123" | chpasswd
    fi
    mkdir -p "/home/$ROLL/solutions" "/home/$ROLL/logs"
    chown -R "$ROLL:$ROLL" "/home/$ROLL"
    chmod 700 "/home/$ROLL"
}

create_student "21BCE123"

echo "Setup Complete. Sandbox user 'sandbox_user' is ready."

# Hardened Polyglot Assessment Platform (HPAP)
## Highly Secure, Database-Free, and AI-Assisted Evaluation Engine

**Architect:** Shaktivel Kumaresan  
**Profile:** Data Engineer | DataOps & Cloud  
**Contact:** shaktivelkumaresan07@gmail.com  
**Affiliation:** B.Tech CSE, SRMIST, Tiruchirappalli  

---

## 1. Project Overview
HPAP is a production-grade automated grading system engineered to deliver high-security coding examinations in academic and professional environments. Moving away from traditional RDBMS dependencies, this project implements a **Filesystem-as-a-State-Store** architecture, optimizing for I/O performance, data portability, and high-security isolation.

The platform supports C, C++, and Python solutions, leveraging Linux kernel primitives and a local Large Language Model (Llama 3) for real-time concept-based student assistance.

---

## 2. Technical Architecture
The system is built on a distributed logic model where state is managed through deterministic directory paths and JSON metadata.

### 2.1 Control Plane: RESTful Orchestration
A Python/Flask backend acts as the unified control plane. It handles:
*   **Request Routing**: Mapping student CLI commands and Admin UI interactions to filesystem operations.
*   **Identity Management**: Integrating with the Linux PAM (Pluggable Authentication Modules) via standard user creation and shadow password management.
*   **Evaluation Scheduling**: Managing concurrent submission queues through unique execution namespaces.

### 2.2 Data Plane: The Linux State Store
Instead of a database, HPAP utilizes the `/srv/assessment_system/` hierarchy:
*   **Assessments Store**: Permanent storage of questions, immutable to the execution layer.
*   **Metadata Engine**: Uses structured `.conf` and `testcases.json` files to drive the polyglot grading pipeline.
*   **Log Aggregation**: Standardized telemetry streams into `backend.log` (system-wide) and `submissions.log` (user-specific), enabling downstream DataOps pipelines for performance analytics.

---

## 3. Security Hardening (Systems Engineering)
The platform is designed to execute untrusted user code with "Bank-Grade" security without the overhead of heavy containerization.

### 3.1 Sandbox Isolation Architecture
*   **Execution Privilege Dropping**: All student code is executed by a dedicated `sandbox_user`. This user is configured with `/usr/sbin/nologin`, no home directory, and zero write permissions on the primary OS tree.
*   **Unique Filesystem Namespaces**: Every evaluation event triggers the creation of a `tempfile.mkdtemp` isolated directory. This prevents cross-contamination and solves race conditions during high-concurrency periods.
*   **Subprocess Decoupling**: The system implements a "Double-Subprocess" model. The Grader runs as a subprocess of the Backend, and the Student Solution runs as a subprocess of the Grader. This prevents memory-space exploits and `sys.modules` tampering.

### 3.2 Kernel-Level Resource Constraints (`rlimit`)
We leverage the Linux `resource` module to set hard limits at the kernel level for every child process:
*   **RLIMIT_CPU**: Hard-cap on CPU time (2s) to mitigate Denial of Service (DoS) via infinite loops.
*   **RLIMIT_AS**: Memory Address Space limitation (256MB) to prevent OOM (Out of Memory) crashes.
*   **RLIMIT_NPROC**: Process count restriction to prevent fork-bomb attacks.
*   **RLIMIT_FSIZE**: File size creation limits to prevent disk-space exhaustion.

---

## 4. AI & DataOps Integration
### 4.1 Local Inference Layer
HPAP integrates **Ollama** running **Llama 3** locally. 
*   **Architecture**: The backend acts as a proxy to the local inference API.
*   **Governance**: A teacher-controlled "Kill-Switch" state is persisted in `active_assessment.conf`. If disabled, the API strictly rejects LLM requests at the gateway level.

### 4.2 Observability & Performance
The system is designed with a **Logs-as-Data** philosophy. Every submission is recorded as a structured log entry, allowing for real-time monitoring of pass/fail rates and system latency, crucial for DataOps engineers monitoring exam health.

---

## 5. Technology Stack
*   **Languages**: Python 3.x, C, C++ (GCC/G++)
*   **Infrastructure**: Linux (RHEL 9 / CentOS / Ubuntu)
*   **Frameworks**: Flask (Backend), Bash (System Integration)
*   **AI**: Ollama, Llama 3
*   **Protocols**: SSH, REST/HTTP

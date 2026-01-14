# 🛡️ InfraOps Guardian

A context-aware RAG (Retrieval-Augmented Generation) assistant for DevOps infrastructure. It allows you to chat with your Terraform code, **visualize architecture diagrams**, maintain **conversational memory**, and perform **security audits**.

## 🚀 Tech Stack (2026 Edition)
- **Language:** Python 3.13
- **Framework:** LangChain 0.3 (Pure LCEL Architecture)
- **LLM:** Google Gemini 2.5 Flash (Adaptive Temperature)
- **Vector DB:** ChromaDB (Local & Persistent)
- **Frontend:** Streamlit (Dual-Mode Interface)
- **Visualization:** Mermaid.js (Auto-rendered)
- **Deployment:** Docker (CPU-Optimized) & GitHub Actions (CI/CD)

## ✨ Key Features

1.  **Dual Operation Modes:**
    * 👷 **Architect Mode:** Helps you understand infrastructure, visualize flows, and draft configurations.
    * 🕵️ **Auditor Mode:** Validates code against CIS Benchmarks, NIST, and PCI-DSS standards using an aggressive retrieval strategy.
2.  **Git Repository Ingestion:** Directly clone and ingest Terraform code from any public GitHub repository.
3.  **Conversational Memory:** Remembers context across multiple queries (e.g., "What about the security group?" -> "Does *it* allow port 22?").
4.  **Source Attribution:** Every answer cites the specific `.tf` file used as a reference.
5.  **Native Visualization:** Generates and renders architecture diagrams on the fly.
6.  **Secure by Default:** Automatically redacts secrets/passwords during ingestion.

---

## 🛠️ Installation & Setup

### Option A: Docker (Recommended)
Running in Docker guarantees an isolated environment with CPU-optimized dependencies.

1.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_google_api_key
    # Optional: Target a specific repo (leave empty for local data)
    GITHUB_REPO_URL="[https://github.com/terraform-aws-modules/terraform-aws-vpc](https://github.com/terraform-aws-modules/terraform-aws-vpc)"
    ```

2.  **Build and Run:**
    ```bash
    docker-compose up --build
    ```
    *The container will automatically handle data ingestion if the database is empty.*

3.  **Access:**
    Open http://localhost:8501

### Option B: Local Development
1.  **Setup Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate   # Windows
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Ingest Data:**
    ```bash
    python src/ingest.py
    ```

4.  **Run Application:**
    ```bash
    python -m streamlit run src/app.py
    ```

---

## 🕵️ Security Auditor Mode (SecOps)

Turn your assistant into a ruthless security auditor with a single click.

1.  **Activate:** Toggle the **"🕵️ Security Auditor Mode"** switch in the sidebar.
2.  **Behavior Change:**
    * **Persona:** Shifts from "Helpful Architect" to "Paranoid Auditor".
    * **Retrieval:** Increases search depth (`k=7`) to find cross-resource vulnerabilities.
    * **Standards:** Analyzes code against **CIS Benchmarks**, **NIST**, and **PCI-DSS**.
3.  **Example Audit Prompts:**
    * *"Perform a vulnerability scan on the Security Groups. Are there open ingress rules?"*
    * *"Does the S3 bucket configuration comply with encryption standards?"*
    * *"Identify any hardcoded credentials or permissive IAM roles."*

---

## 🎯 Demo Scenarios

Use these scenarios to test the capabilities using the `terraform-aws-vpc` module or your own code.

### 🔍 Complex Logic Analysis
* *"What variable controls whether a single NAT Gateway is used for all zones? What is its default value?"*
* *"Explain the logic used to create private subnets. Which Terraform resource is used?"*

### 📊 Architecture Visualization
* *"Generate a Mermaid diagram showing the relationship between the VPC, Public Subnets, and the Internet Gateway."*
* *"Visualize the decision flow for enabling VPN Gateway."*

### 📜 Source Audit
* *"Where is the CIDR block defined?"*
    * *✅ Success:* The bot should reply "According to **variables.tf**..." and list the file in the sources.

---

## 🧑‍💻 Engineering Standards & CI/CD

This project is built with strict quality gates enforced by **GitHub Actions**:

* **Linting:** `black` (Formatting) & `isort` (Imports).
* **Type Safety:** `mypy` (Strict Static Typing).
* **Testing:** `pytest` suite with Mocking for Git and Database checks.
* **Docker Optimization:** The build pipeline forces `torch` CPU-only version, reducing image size from **~8GB to <1GB**.

To run checks locally:
```bash
# Format code
./venv/Scripts/python -m black .
./venv/Scripts/python -m isort .

# Run tests
pytest
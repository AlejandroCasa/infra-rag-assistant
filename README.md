# 🛡️ InfraOps Guardian

A context-aware RAG (Retrieval-Augmented Generation) assistant for DevOps infrastructure. It allows you to chat with your Terraform code, **visualize architecture diagrams**, and maintains **conversational memory**.

## 🚀 Tech Stack (2026 Edition)
- **Language:** Python 3.13
- **Framework:** LangChain 0.3 (Pure LCEL)
- **LLM:** Google Gemini 2.5 Flash
- **Vector DB:** ChromaDB (Local & Dockerized)
- **Frontend:** Streamlit
- **Visualization:** Mermaid.js (Auto-rendered)
- **Deployment:** Docker & Docker Compose

## 🛠️ Installation & Setup

### Option A: Docker (Recommended)
The easiest way to run the full stack (App + DB) in an isolated environment.

1. **Build and Run:**
   ```bash
   docker-compose up --build
Access: Open http://localhost:8501

Option B: Local Python Dev
Setup Environment:

Bash

python -m venv venv
./venv/Scripts/activate  # Windows
pip install -r requirements.txt
Ingest Data:

Bash

python src/ingest.py
Run App:

Bash

python -m streamlit run src/app.py
🛠️ GitHub Repository Ingestion (New Feature)
You can now ingest Terraform files directly from a public GitHub repository instead of a local folder.

Configure the Repo: Create or update your .env file with the target repository URL:

Bash

# Example: Complex AWS VPC Module
GITHUB_REPO_URL="[https://github.com/terraform-aws-modules/terraform-aws-vpc](https://github.com/terraform-aws-modules/terraform-aws-vpc)"
(Note: Remove this line or leave it empty to fallback to local data/ folder)

Run Ingestion:

Bash

python src/ingest.py
This will clone the repo, process all .tf files, and update the vector database.

🎯 Demo Scenarios & Prompts
Use these scenarios to validate the specific features of the assistant.

Scenario A: Complex Logic Analysis (using AWS VPC Repo)
Target Repo: terraform-aws-modules/terraform-aws-vpc

Understanding Variables:

"What variable controls whether a single NAT Gateway is used for all zones? What is its default value?"

Conditional Logic:

"Explain the logic used to create private subnets. Which Terraform resource is used?"

Outputs:

"List the critical outputs exposed by this module that I would need to connect an EKS cluster."

Scenario B: Architecture Visualization
Topology:

"Generate a Mermaid diagram showing the relationship between the VPC, Public Subnets, and the Internet Gateway."

Flow:

"Visualize the decision flow for enabling VPN Gateway."

Scenario C: Audit & Citations
Source Attribution:

"Where is the CIDR block defined?" ✅ Success: The bot should reply "According to variables.tf..." and list the file in the sources.

🧑‍💻 Quality Assurance
This project adheres to strict coding standards. To verify the codebase:

Bash

# Format Code
black . && isort .

# Static Type Checking
mypy src/

# Run Unit Tests
pytest
🧠 Project Status
✅ Dockerized: Works on Windows/Linux/Mac.

✅ Memory: Remembers previous questions.

✅ Visuals: Native diagram rendering.

✅ Secure: Auto-redaction of secrets during ingestion.

✅ Git Integration: Ingest directly from GitHub URLs.

✅ Auditable: Answers cite specific source files.

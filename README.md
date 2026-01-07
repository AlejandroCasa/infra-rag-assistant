# 🛡️ InfraOps Guardian

A RAG (Retrieval-Augmented Generation) assistant for DevOps infrastructure, capable of answering questions and **visualizing architecture** based on your Terraform code.

## 🚀 Tech Stack (2026 Edition)
- **Language:** Python 3.13
- **Framework:** LangChain 0.3 (Pure LCEL Architecture)
- **LLM:** Google Gemini 2.5 Flash
- **Vector DB:** ChromaDB (Local)
- **Frontend:** Streamlit
- **Visualization:** Mermaid.js (Auto-rendered)
- **Deployment:** Docker & Docker Compose

## 🛠️ Installation & Setup

### Option A: Local Development (Python)

1. **Clone and setup environment:**
   ```bash
   python -m venv venv
   # Windows
   ./venv/Scripts/activate
   # Mac/Linux
   source venv/bin/activate

   pip install -r requirements.txt

```

2. **Configure Secrets:**
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_api_key_here

```


3. **Ingest Data (Memory):**
Place your `.tf` files in `data/terraform_sample/` and run:
```bash
python src/ingest.py

```


4. **Launch App:**
```bash
python -m streamlit run src/app.py

```



### Option B: Docker (Recommended for Deployment)

Run the application in an isolated container without installing Python locally.

1. **Build and Run:**
```bash
docker-compose up --build

```


2. **Access:**
Open http://localhost:8501

## 🎯 Example Queries

Try these prompts to see the full power of the assistant:

### 🔍 Information Retrieval (Text)

* *"What is the instance type of the web server?"*
* *"What ports are allowed in the security group `web_sg`?"*
* *"List all S3 buckets and check if versioning is enabled."*
* *"Is the database publicly accessible?"*

### 📊 Architecture Visualization (Diagrams)

* *"Generate a diagram showing the connection between the security groups and the instances."*
* *"Visualize the network traffic flow for the web server (Ingress/Egress)."*
* *"Draw a graph showing the dependency between the EC2 instance and the S3 bucket."*
* *"Create a flowchart of the security group rules."*

## 🧠 Project Status

* ✅ Python 3.13 Support (Legacy `langchain.chains` removed).
* ✅ Integrated with Gemini 2.5 Flash (State-of-the-Art).
* ✅ Automatic ingestion of new Terraform resources.
* ✅ **Native Mermaid.js support** for architecture diagrams.
* ✅ Dockerized for easy deployment.

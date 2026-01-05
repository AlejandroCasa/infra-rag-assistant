# 🛡️ InfraOps Guardian

A RAG (Retrieval-Augmented Generation) assistant for DevOps infrastructure, capable of answering questions about your Terraform code.

## 🚀 Tech Stack (2026 Edition)
- **Language:** Python 3.13
- **Framework:** LangChain 0.3 (Pure LCEL Architecture)
- **LLM:** Google Gemini 2.5 Flash
- **Vector DB:** ChromaDB (Local)
- **Frontend:** Streamlit

## 🛠️ Installation

1. **Clone and setup environment:**
   ```bash
   python -m venv venv
   ./venv/Scripts/activate
   pip install -r requirements.txt

```

2. **Configure Secrets:**
Create a `.env` file with your API key:
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



## 🧠 Project Status

* ✅ Python 3.13 Support (Legacy `langchain.chains` removed).
* ✅ Integrated with Gemini 2.5 Flash (State-of-the-Art).
* ✅ Automatic ingestion of new Terraform resources.
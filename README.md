# RAG Advanced Chatbot

An AI-powered chatbot with **3 processing branches**:
- **Troubleshoot**: Searches for technical issue solutions via **Tavily Search API**.  
- **English Practice**: Solves English exercises from PDF files (using **VectorDB + Embeddings**).  
- **General**: Handles casual conversation and general knowledge questions.  

The chatbot also maintains **conversation history (memory)** to provide context-aware responses.

---

## 📂 Project Structure

rag_advanced/
├─ init.py # empty file so Python treats this as a package
├─ app.py # CLI / main entrypoint
├─ config.py # Load environment variables, init LLM & Embeddings
├─ prompts.py # System prompts (Classifier, Solve, General)
├─ utils.py # Helper functions: clean text, chunk text, build context
├─ retrieval.py # PDF handling + Chroma VectorDB
├─ chains.py # Define chains: classifier, tavily, vectordb, general
├─ router.py # Routing logic → choose chain based on label
└─ requirements.txt # Dependencies

yaml
Sao chép
Chỉnh sửa

---

## ⚙️ Setup

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
Install dependencies:

powershell
Sao chép
Chỉnh sửa
pip install -r requirements.txt
Create a .env file in the project root:

env
Sao chép
Chỉnh sửa
OPENAI__API_KEY=your_openai_api_key
OPENAI__EMBEDDING_MODEL=text-embedding-3-small
OPENAI__MODEL_NAME=gpt-4o-mini
OPENAI__TEMPERATURE=0
TAVILY_API_KEY=your_tavily_api_key
Make sure you have a PDF file to use, and update the path in retrieval.py:

python
Sao chép
Chỉnh sửa
PDF_PATH = r"C:\path\to\your\pdf_file.pdf"
▶️ Running the Chatbot
Important: Because this project is structured as a package, you must run it with -m.

From the parent directory (the folder containing rag_advanced/):

powershell
Sao chép
Chỉnh sửa
python -m rag_advanced.app
You’ll see:

pgsql
Sao chép
Chỉnh sửa
Chatbot with 3 branches (Tavily + PDF + General) and memory support.
Type 'exit' to quit, 'clear' to reset conversation history.
🧑‍💻 Usage Examples
Troubleshoot: ask about technical issues → bot will use Tavily.

vbnet
Sao chép
Chỉnh sửa
> You: Cannot connect to VPN, error "auth failed"
English Practice: ask questions/exercises related to English → bot will retrieve from PDF and solve step by step.

mathematica
Sao chép
Chỉnh sửa
> You: Solve the past perfect exercise in the PDF
General: casual talk or general knowledge.

markdown
Sao chép
Chỉnh sửa
> You: What’s the weather like today?
❗ Import Notes
If you see an error like:

pgsql
Sao chép
Chỉnh sửa
ImportError: attempted relative import with no known parent package
it’s because you ran app.py directly.

✅ Correct way: always run with -m from the parent directory:

powershell
Sao chép
Chỉnh sửa
python -m rag_advanced.app
If you must run python app.py directly, change imports from:

python
Sao chép
Chỉnh sửa
from .chains import make_chatbot
to:

python
Sao chép
Chỉnh sửa
from chains import make_chatbot
(But this is not recommended.)

📦 Main Dependencies
langchain-core

langchain-openai

langchain-community

langchain-chroma

pypdf

requests

python-dotenv

✅ Key Features
Smart classifier (3 labels: troubleshoot, english_practice, general).

PDF knowledge extraction with VectorDB + Embeddings.

Web search via Tavily API.

Memory to maintain conversation history.

Router automatically chooses the correct branch.

🚀 Future Improvements
Allow dynamic PDF upload instead of fixed path.

Add web UI (FastAPI + Streamlit).

Save conversation logs to a database.

yaml
Sao chép
Chỉnh sửa

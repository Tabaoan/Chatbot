import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv(override=True)

OPENAI__API_KEY = os.getenv("OPENAI__API_KEY")
OPENAI__EMBEDDING_MODEL = os.getenv("OPENAI__EMBEDDING_MODEL")
OPENAI__MODEL_NAME = os.getenv("OPENAI__MODEL_NAME")
OPENAI__TEMPERATURE = float(os.getenv("OPENAI__TEMPERATURE") or 0)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

llm = ChatOpenAI(
    api_key=OPENAI__API_KEY,
    model_name=OPENAI__MODEL_NAME,
    temperature=OPENAI__TEMPERATURE,
)

embeddings = OpenAIEmbeddings(
    api_key=OPENAI__API_KEY,
    model=OPENAI__EMBEDDING_MODEL,
)

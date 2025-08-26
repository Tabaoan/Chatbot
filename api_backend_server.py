# api_backend_server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os

# Import chatbot từ file bạn đã tạo (đổi 'app' nếu khác tên)
from app1 import chatbot

app = FastAPI(title="Chatbot API", description="2-branch Chatbot with Tavily & PDF")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

executor = ThreadPoolExecutor(max_workers=4)

# Trả về index.html nếu có, không cần thư mục static
@app.get("/", response_class=HTMLResponse)
async def read_root():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h3>FastAPI is running. POST /chat to talk to the bot.</h3>")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: chatbot.invoke(
                {"message": request.message},
                config={"configurable": {"session_id": request.session_id}}
            )
        )
        return ChatResponse(response=result, session_id=request.session_id)
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Bind trực tiếp vào localhost
    uvicorn.run(
        "api_backend_server:app",
        host="127.0.0.1",  
        port=8000,
        reload=True,
        log_level="info"
    )

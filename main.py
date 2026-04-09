import uvicorn
from dotenv import load_dotenv
load_dotenv()
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.memory import InMemorySaver
import prompts
from base_tools import live_web_search

checkpointer = InMemorySaver()
tools_list = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    global tools_list
    tools_list = [live_web_search]
    print("Tools are loaded.. Ready to create the agent..") 
    yield

app = FastAPI(lifespan=lifespan)

#Pydantic Data Model
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    model: str = "gemini-2.5-flash"
    thread_id: str = "default"

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_response_stream(query, model_name, thread_id):
    #Initialize Model and Agent
    system_prompt = prompts.CHAT_ASSISTANT_PROMPT
    model = ChatGoogleGenerativeAI(model = model_name)
    agent = create_agent(model=model, system_prompt=system_prompt,tools=tools_list,checkpointer=checkpointer)
    config = {'configurable':{'thread_id':thread_id}}
    async for chunk,metadata in agent.astream(
        {'messages':[HumanMessage(content=query)]},stream_mode='messages',config=config):
        data = {'type': chunk.__class__.__name__,
                'content': chunk.text
                }
        print("^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(data)

        yield (json.dumps(data)+"\n").encode()

def main():
    print("Hello from ai-agent-project!")
    
@app.get("/")
async def read_root():
    return "Shree Gurubyoh Namah!Namah Shankaraya!"

@app.post("/chat_stream")
async def chat_stream(request: ChatRequest):
    print("Its coming here...........")
    if not request.query.strip():
        raise HTTPException(status_code=400,detail="Empty prompt! Please enter a valid prompt..")
    
    try:
        
        return StreamingResponse(get_response_stream(request.query,request.model,
            request.thread_id), media_type = "application/x-ndjson")
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")


if __name__ == "__main__":    
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
    main()

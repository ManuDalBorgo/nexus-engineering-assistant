from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Nexus Engineering Assistant API", version="0.1.0")

class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Nexus API is running"}

@app.post("/agent/query")
def query_agent(request: QueryRequest):
    try:
        # Import here to avoid circular dependencies or path issues during startup
        from backend.app.agents.orchestrator import NexusOrchestrator
        
        # Initialize agent (defaults to Anthropic/OpenAI based on env)
        agent = NexusOrchestrator(model_provider="anthropic")
        
        # Get response (using the non-streaming method for REST API)
        response = agent.process_request(request.query)
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

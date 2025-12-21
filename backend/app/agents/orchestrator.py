import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser

class NexusOrchestrator:
    def __init__(self, model_provider="local"):
        self.model_provider = model_provider
        self.llm = self._get_llm()

    def _get_llm(self):
        if self.model_provider == "openai":
            return ChatOpenAI(model="gpt-4o", temperature=0)
        elif self.model_provider == "anthropic":
            return ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0, max_tokens=4096)
        elif self.model_provider == "devstral":
             # Best open-source agentic coding model
            return ChatOllama(model="devstral-small-2", temperature=0)
        elif self.model_provider == "local_fast":
             # Lightweight coding model (7B)
            return ChatOllama(model="qwen2.5-coder:7b", temperature=0)
        elif self.model_provider == "mistral_api":
             # Cloud API for speed + smarts
            return ChatMistralAI(model="mistral-large-latest", temperature=0)
        elif self.model_provider == "local":
            # Assumes the user has pulled the model: `ollama pull llama3`
            return ChatOllama(model="llama3", temperature=0)
        else:
            return ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0, max_tokens=4096)

    def process_request(self, user_query: str):
        """
        Analyzes the user request and routes it to the appropriate sub-agents.
        """
        # 1. Retrieve Context
        from backend.app.rag.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        retriever = kb.get_retriever()
        docs = retriever.get_relevant_documents(user_query)
        context = "\n\n".join([d.page_content for d in docs])

        # 2. Generate Response with Context
        prompt = ChatPromptTemplate.from_template(
            """
            You are Nexus, an expert AI Solutions Architect and Hardware Engineer at ARM.
            Your goal is to assist engineers with designing and verifying semiconductor IP.
            
            Context from AMBA Specs:
            {context}
            
            User Request: {query}
            
            If the request is about generating code (Verilog/SystemVerilog), provide a professional, commented code block.
            Ensure you follow the protocols defined in the context.
            If the request is a question, answer it with technical precision.
            
            Response:
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({"query": user_query, "context": context})
        except Exception as e:
            error_msg = str(e)
            if "Connection refused" in error_msg or "Errno 61" in error_msg:
                return (
                    "**Error: Could not connect to the Local LLM.**\n\n"
                    "It looks like **Ollama** is not running or not installed.\n"
                    "1. Make sure you have installed Ollama from [ollama.com](https://ollama.com).\n"
                    "2. Run `ollama serve` in a terminal.\n"
                    "3. Ensure you have the model: `ollama pull qwen2.5-coder:7b` (for speed) or `ollama pull devstral-small-2` (for smarts).\n"
                    "4. Or, switch to **Claude/Mistral API**."
                )
            return f"Error connecting to LLM: {error_msg}. Please ensure API keys are set in .env."

    def stream_request(self, user_query: str):
        """
        Streams the response from the LLM, including intermediate steps.
        """
        # 1. Retrieve Context
        yield {"type": "step", "content": "🔍 Orchestrator: Analyzing intent..."}
        
        from backend.app.rag.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        retriever = kb.get_retriever()
        
        yield {"type": "step", "content": "📚 RAG Agent: Searching knowledge base for protocol specs..."}
        docs = retriever.get_relevant_documents(user_query)
        context = "\n\n".join([d.page_content for d in docs])
        
        # Show what was found (briefly)
        if docs:
            snippet = docs[0].page_content[:100] + "..."
            yield {"type": "step", "content": f"✅ Found relevant specs: {snippet}"}

        # 2. Generate Response with Context
        yield {"type": "step", "content": "⚙️ RTL Agent: Generating Verilog code..."}
        
        prompt = ChatPromptTemplate.from_template(
            """
            You are Nexus, an expert AI Solutions Architect and Hardware Engineer at ARM.
            Your goal is to assist engineers with designing and verifying semiconductor IP.
            
            Context from AMBA Specs:
            {context}
            
            User Request: {query}
            
            If the request is about generating code (Verilog/SystemVerilog), provide a professional, commented code block.
            Ensure you follow the protocols defined in the context.
            If the request is a question, answer it with technical precision.
            
            Response:
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            for chunk in chain.stream({"query": user_query, "context": context}):
                yield {"type": "token", "content": chunk}
        except Exception as e:
            error_msg = str(e)
            if "Connection refused" in error_msg or "Errno 61" in error_msg:
                friendly_msg = (
                    "\n\n**⚠️ Error: Could not connect to the Local LLM (Ollama).**\n\n"
                    "To use the 'Local' option, you must have **Ollama** running in the background.\n"
                    "1.  **Install Ollama**: [Download here](https://ollama.com)\n"
                    "2.  **Start it**: Run `ollama serve` in a terminal or open the app.\n"
                    "3.  **Pull the model**: Run `ollama pull qwen2.5-coder:7b`.\n\n"
                    "👉 *Switch to an API provider (Claude/Mistral) if your local machine is too slow.*"
                )
                yield {"type": "error", "content": friendly_msg}
            else:
                yield {"type": "error", "content": f"Error: {error_msg}"}

# Simple test
if __name__ == "__main__":
    agent = NexusOrchestrator()
    print(agent.process_request("Explain the AXI handshake"))

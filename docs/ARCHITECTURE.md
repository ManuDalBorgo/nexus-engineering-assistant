# System Architecture

## Component Diagram

```mermaid
graph TD
    User[User / Engineer] -->|Browser| UI[Streamlit Interface]
    UI -->|Direct Import / API| Orchestrator[Orchestrator Agent]
    
    subgraph "Nexus Core (Python)"
        Orchestrator -->|Task: Research| RAG[Knowledge Agent]
        Orchestrator -->|Task: Code| Coder[RTL Generator Agent]
        Orchestrator -->|Task: Verify| Verifier[Verification Agent]
        
        RAG <-->|Query/Retrieve| VectorDB[(ChromaDB)]
        
        Coder -->|Draft Code| Guardrails[Syntax & Lint Checker]
        Guardrails -->|Feedback| Coder
    end
    
    subgraph "External Services"
        LLM[LLM Provider (Gemini/GPT/Claude)]
    end
    
    Orchestrator -.-> LLM
    RAG -.-> LLM
    Coder -.-> LLM
    Verifier -.-> LLM
```

## Data Flow

1.  **Request Ingestion**: The User submits a prompt via the UI.
2.  **Intent Classification**: The Orchestrator analyzes the prompt to determine if it requires RAG (information lookup) or Generation (coding).
3.  **Context Retrieval**: If technical details are needed (e.g., "AXI4 burst types"), the Knowledge Agent queries the VectorDB.
4.  **Generation**: The RTL Generator Agent constructs the code, utilizing the retrieved context to ensure protocol compliance.
5.  **Validation**: The generated code is passed through a static analysis layer (simulated or real `verilator` linting).
6.  **Response**: The final artifacts (Code, Explanations, Testbenches) are streamed back to the UI.

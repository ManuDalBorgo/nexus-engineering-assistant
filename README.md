# Nexus: The AI-Powered Semiconductor Engineering Assistant

## Project Overview
**Nexus** is a proof-of-concept **Agentic AI Platform** designed to demonstrate the future of engineering at **Arm**. It serves as an intelligent co-pilot for hardware architects and verification engineers, automating the translation of high-level specifications into compliant RTL designs and verification plans.

This project was built to showcase the capabilities required for the **AI Solutions Architect** role, specifically focusing on:
- **Agentic AI**: Multi-agent orchestration for complex problem solving (Planning, Coding, Reviewing).
- **RAG (Retrieval-Augmented Generation)**: Context-aware answers based on technical specifications (e.g., AMBA AXI, ARMv9).
- **Guardrails & Evaluation**: Ensuring generated code meets strict syntax and safety standards.
- **Scalable Architecture**: A modular design ready for enterprise deployment.

## Solution Architecture

### High-Level Design
Nexus operates on a **Hub-and-Spoke Agentic Architecture**:

1.  **Orchestrator Agent (The "Lead")**: Deconstructs user requests (e.g., "Create an AXI4-Lite Slave module") into sub-tasks.
2.  **Knowledge Agent (The "Researcher")**: Uses RAG to retrieve precise protocol constraints from indexed documentation.
3.  **RTL Agent (The "Implementer")**: Generates Verilog/SystemVerilog code based on requirements and retrieved context.
4.  **Verification Agent (The "Tester")**: Generates UVM testbench skeletons and SystemVerilog Assertions (SVA) to verify the design.
5.  **Guardrails Layer**: Static analysis tools (linting) to validate outputs before presenting them to the user.

### Technology Stack
- **Core Logic**: Python 3.10+
- **LLM Orchestration**: LangChain / LangGraph
- **Vector Database**: ChromaDB (for RAG)
- **API Interface**: FastAPI
- **Frontend**: Streamlit (for rapid, interactive prototyping).

## Core Concepts Explained

### 1. Model Strategy: Specialized for Software Engineering
Unlike generic chatbots (like standard Llama 3 or GPT-4), we utilize models **specifically fine-tuned for code and engineering tasks**:

*   **Devstral Small 2 24B**:
    *   *Specialization*: **Agentic Software Engineering**.
    *   *Why?*: Designed by Mistral AI specifically to power software agents. It is trained to understand file structures, diffs, and complex tool usage, making it far superior to generic models for tasks like "refactor this module" or "write a test plan".
    
*   **Qwen 2.5 Coder 7B**:
    *   *Specialization*: **High-Performance Coding**.
    *   *Why?*: A purpose-built coding model that rivals GPT-4 on coding benchmarks (HumanEval) despite its small size. It is not a general-purpose chat model; its weights are optimized purely for understanding and generating programming languages (Verilog, Python, C++).

### 2. Orchestrated (The "Brain")
The **NexusOrchestrator** serves as the central manager. It receives raw engineering requests, analyzes the intent, and systematically coordinates the underlying agents. Instead of a simple chatbot response, the system breaks down complex tasks, calls the RAG system for context, and then constructs the final prompt for the LLM. This demonstrates a true **Agentic Workflow**.

### 3. RAG (Retrieval-Augmented Generation)
To prevent "hallucinations" and ensure technical accuracy, Nexus uses a Retrieval-Augmented Generation architecture. The system ingests the **AMBA AXI4 Protocol Specifications** into a local vector database (`ChromaDB`). When a user requests an "AXI Slave," the system searches this database, retrieves the exact signal definitions (e.g., `AWVALID`, `WREADY`), and grounds its response in Arm's official documentation.

> **Why RAG is Critical for Hardware**:
> Unlike software languages (Python/JS) where training data is abundant, high-quality open-source datasets for hardware protocols (AXI, CHI, ACE) are scarce. Most models, including Devstral, haven't seen enough Verilog training data to memorize these specs perfectly. Nexus solves this by "injecting" the knowledge at runtime via RAG, allowing even smaller models to generate protocol-compliant hardware.

### 3. RTL (Register Transfer Level)
The **RTL Generator** persona takes the retrieved specifications and produces synthesizable Verilog/SystemVerilog code. This automates the creation of boilerplate hardware logic, allowing engineers to focus on high-level architecture rather than repetitive coding tasks.

### 4. Verified (Quality Control)
Design is incomplete without verification. The **Verification Expert** agent capability ensures that generated designs are testable. Nexus can generate SystemVerilog testbenches (UVM or simple) alongside the design, acknowledging that verification often consumes the majority of the engineering effort.

## Use Case: Accelerating IP Development
**Scenario**: An engineer needs a customized **APB (Advanced Peripheral Bus) Bridge**.

1.  **Input**: Engineer types: *"Generate an APB bridge with 32-bit data width and PREADY support."*
2.  **Process**:
    - *Orchestrator* parses intent.
    - *Knowledge Agent* looks up APB protocol specs for signal timing.
    - *RTL Agent* writes the Verilog module.
    - *Verification Agent* creates a testbench to check `PENABLE` and `PSEL` timing.
3.  **Output**: A fully formed, lint-checked code snippet + verification plan.

## Local Model Setup (Optional but Recommended)
To run fully locally without API keys:
1.  **Install Ollama**: Download and install from [ollama.com](https://ollama.com/).
    > **Note**: You *must* install the Ollama application manually. The script cannot do this for you.
2.  **Pull the Model**: The `run_demo.sh` script will attempt to auto-pull `devstral-small-2` if Ollama is installed. You can also do it manually:
    ```bash
    ollama pull devstral-small-2
    ```
3.  In the Nexus UI, select **"Local (Ollama - Devstral)"** from the dropdown (this is now default).

## Data Ingestion (RAG)
To populate the Knowledge Base with the latest specs:
```bash
python3 ingest_data.py
```
This will read all text files in `backend/data/specs`, chunk them, and store embeddings in `backend/data/chroma_db`.

Nexus directly addresses this by:
- **Reducing Boilerplate**: Automating repetitive coding tasks.
- **Democratizing Knowledge**: Making complex specs instantly queryable.
- **Ensuring Quality**: Embedding verification early in the design loop.

---
## Sample Outputs
See [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md) for a full transcript of a live session generating an AXI4-Lite Slave module.

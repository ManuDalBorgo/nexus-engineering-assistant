import streamlit as st
import time

st.set_page_config(
    page_title="Nexus | ARM Engineering Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stSidebar {
        background-color: #262730;
    }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #0091BD; /* ARM Blue-ish */
    }
    .stButton>button {
        background-color: #0091BD;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stChatMessage {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Nexus: Intelligent Engineering Co-Pilot")
st.markdown("### Accelerating Semiconductor Design with Agentic AI")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    # Added "Local (Ollama)" to the list
    # Added "Local (Ollama)" to the list
    model_options = [
        "Local Fast (Ollama - Qwen 2.5 7B)", 
        "Local Strong (Ollama - Devstral 24B)",
        "Mistral API (Cloud)",
        "Claude Sonnet 4", 
        "GPT-4o"
    ]
    model_choice = st.selectbox("Model", model_options, index=0)
    
    # Map selection to provider ID
    provider_map = {
        "Local Fast (Ollama - Qwen 2.5 7B)": "local_fast",
        "Local Strong (Ollama - Devstral 24B)": "devstral",
        "Mistral API (Cloud)": "mistral_api",
        "Claude Sonnet 4": "anthropic",
        "GPT-4o": "openai"
    }
    selected_provider = provider_map[model_choice]

    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.2)
    st.divider()
    st.markdown("**Active Agents:**")
    st.checkbox("Orchestrator", value=True, disabled=True)
    st.checkbox("RAG (Knowledge)", value=True)
    st.checkbox("RTL Generator", value=True)
    st.checkbox("Verification Expert", value=True)

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Nexus. I can assist you with ARM architecture queries, RTL generation, and verification planning. How can I help you today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Describe your design requirement (e.g., 'Generate an AXI4-Lite Slave module')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Simulation of agent thought process
        with st.status("Thinking...", expanded=True) as status:
            st.write("Orchestrator: Analyzing intent...")
            
            # CALL REAL BACKEND
            try:
                # We need to add the project root to sys.path to import backend
                import sys
                import os
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                
                from backend.app.agents.orchestrator import NexusOrchestrator
                
                # Initialize Agent with selected provider
                agent = NexusOrchestrator(model_provider=selected_provider)
                
                # Stream the response with intermediate steps
                response_stream = agent.stream_request(prompt)
                
                full_response = ""
                response_placeholder = st.empty()
                
                for event in response_stream:
                    if event["type"] == "step":
                        st.write(event["content"])
                        time.sleep(0.5) # Small delay to make it readable
                    elif event["type"] == "token":
                        full_response += event["content"]
                        response_placeholder.markdown(full_response + "▌")
                    elif event["type"] == "error":
                        st.error(event["content"])
                
                response_placeholder.markdown(full_response)
                
                status.update(label="Complete!", state="complete", expanded=False)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                status.update(label="Error", state="error", expanded=False)
                st.error(f"An error occurred: {str(e)}")
                st.info("Make sure you have set your API keys in a .env file!")

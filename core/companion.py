# core/companion.py
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)

def initialize_code_companion():
    """Initialize session state for code companion"""
    if "message_log" not in st.session_state:
        st.session_state.message_log = [
            {"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today? 💻"}
        ]
    if "model" not in st.session_state:
        st.session_state.model = "deepseek-r1:1.5b"

def render_sidebar():
    """Render the sidebar components"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.session_state.model = st.selectbox(
            "Choose Model",
            ["deepseek-r1:1.5b", "deepseek-r1:3b"],
            index=0
        )
        st.divider()
        st.markdown("### Model Capabilities")
        st.markdown("""
            - 🐍 Python Expert
            - 🐞 Debugging Assistant
            - 📝 Code Documentation
            - 💡 Solution Design
        """)
        st.divider()
        st.markdown("Built with [Ollama](https://ollama.ai/) | [LangChain](https://python.langchain.com/)")

def escape_curly_braces(content: str) -> str:
    """Escape curly braces in content for prompt templates"""
    return content.replace("{", "{{").replace("}", "}}")

def build_prompt_chain() -> ChatPromptTemplate:
    """Construct the conversation prompt chain"""
    system_prompt = SystemMessagePromptTemplate.from_template(
        "You are an AI assistant that provides accurate answers for programming, debugging and general queries. "
        "When answering technical questions, provide step-by-step explanations and practical examples. "
        "If a PDF is uploaded, analyze its content before answering related questions. "
        "If a question lacks clarity, ask for more details. Always provide responses that are clear, logical, and useful.Always response in English"
    )
    
    
    prompt_sequence = [system_prompt]
    
    for msg in st.session_state.message_log:
        escaped_content = escape_curly_braces(msg["content"])
        
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(escaped_content))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(escaped_content))
    
    return ChatPromptTemplate.from_messages(prompt_sequence)

def generate_response(user_query: str):
    """Generate and handle AI responses"""
    try:
        llm = ChatOllama(
            model=st.session_state.model,
            base_url="http://localhost:11434",
            temperature=0.3
        )
        
        prompt_chain = build_prompt_chain()
        processing_pipeline = prompt_chain | llm | StrOutputParser()
        
        return processing_pipeline.invoke({})
        
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

def render_chat_interface():
    """Main chat interface component"""
    st.title("🧠 DeepSeek Code Companion")
    st.caption("🚀 Your AI Pair Programmer with Debugging Superpowers")
    
    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.message_log:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # User input handling
    if user_query := st.chat_input("Type your coding question here..."):
        st.session_state.message_log.append({"role": "user", "content": user_query})
        
        with st.spinner("🧠 Processing..."):
            ai_response = generate_response(user_query)
        
        st.session_state.message_log.append({"role": "ai", "content": ai_response})
        st.rerun()

def code_companion_interface():
    """Main entry point for code companion"""
    initialize_code_companion()
    render_sidebar()
    render_chat_interface()
    
    # Custom CSS injection
    st.markdown("""
    <style>
        .main { background-color: #1a1a1a; color: #fff }
        .sidebar .sidebar-content { background-color: #2d2d2d }
        .stTextInput textarea { color: #fff !important }
        .stSelectbox div[data-baseweb="select"] { 
            color: white !important;
            background-color: #3d3d3d !important;
        }
        .stSelectbox svg { fill: white !important }
        .stSelectbox option { 
            background-color: #2d2d2d !important;
            color: white !important;
        }
        div[role="listbox"] div { 
            background-color: #2d2d2d !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
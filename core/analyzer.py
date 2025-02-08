import streamlit as st
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

class DocumentAnalyzer:
    def __init__(self):
        # Correctly initialize OllamaEmbeddings
        self.embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
        
        # FIX: Pass embedding model to InMemoryVectorStore
        self.vector_db = InMemoryVectorStore(embedding=self.embeddings)

        self.PROMPT_TEMPLATE = """Answer based on context:\n\n{context}\n\nQuestion: {query}"""

        if "docs_processed" not in st.session_state:
            st.session_state.docs_processed = False

    def process_uploaded_file(self, uploaded_file):
        """Handle PDF processing"""
        with st.spinner("Processing document..."):
            # Save uploaded file to a temporary location for PDFPlumberLoader
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.read())

            loader = PDFPlumberLoader("temp_uploaded.pdf")  # Fix: Use file path
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)

            # Convert text to embeddings and store in vector DB
            self.vector_db.add_documents(chunks)

            st.session_state.docs_processed = True

    def query_documents(self, question):
        """Handle document queries"""
        if not st.session_state.docs_processed:
            return "Please upload a document first"
        
        # Search similar documents
        docs = self.vector_db.similarity_search(question, k=3)  # Top 3 matches
        context = "\n".join([d.page_content for d in docs])  # Fix: Access `page_content` correctly

        llm = ChatOllama(model="deepseek-r1:1.5b")
        prompt = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)

        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"context": context, "query": question})

def document_analyzer_interface():
    """Document analysis UI component"""
    st.title("📘 Document Analyzer")
    analyzer = DocumentAnalyzer()

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        analyzer.process_uploaded_file(uploaded_file)

    if query := st.chat_input("Ask about the document..."):
        response = analyzer.query_documents(query)
        st.chat_message("assistant").markdown(response)

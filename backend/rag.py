import os
import shutil
from typing import List
from uuid import uuid4

from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

# Global variables
embedding_function = None
vectorstore = None
retriever = None
rag_chain = None

def initialize_rag():
    global embedding_function, vectorstore, retriever, rag_chain
    global template, prompt, llm # Correctly placed at top
    try:
        print("Initializing RAG...")

        # 1. Embeddings (Local - No API Key)
        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        DB_PATH = "faiss_index_local"

        # 2. Vector Store
        try:
            if os.path.exists(DB_PATH):
                vectorstore = FAISS.load_local(DB_PATH, embedding_function, allow_dangerous_deserialization=True)
                print("Loaded existing vector store.")
            else:
                vectorstore = FAISS.from_texts(["Welcome to the Study Assistant!"], embedding_function)
                vectorstore.save_local(DB_PATH)
                print("Created new vector store.")
        except Exception as e:
            print(f"VectorStore Init Error (Ignored): {e}")
            vectorstore = FAISS.from_texts(["Recall fallback"], embedding_function)

        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # 3. LLM (Groq)
        if not os.environ.get("GROQ_API_KEY"):
            print("CRITICAL: GROQ_API_KEY missing.")
            return

        # 4. Prompt & LLM

        template = """You are a helpful Study Assistant.
Answer the question based ONLY on the following context.
If the answer is not in the context, say "I couldn't find that in your notes."
Always mention the source of your information.

Context:
{context}

Question:
{question}

Answer:
"""
        prompt = ChatPromptTemplate.from_template(template)
        
        # Define LLM here so it's initialized
        llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0.3
        )
        
        create_rag_chain()
        
        print("RAG System Initialized Successfully (Groq + Local Embeddings).")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to initialize RAG: {e}")

def format_docs(docs):
     # Format as: Content (Source: filename)
     return "\n\n".join(f"{doc.page_content}\n(Source: {doc.metadata.get('source', 'Unknown')})" for doc in docs)

def create_rag_chain():
    global rag_chain, retriever, prompt, llm
    if not retriever or not llm: return

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG Chain Rebuilt.")

# Attempt initialization
initialize_rag()

# Modified for Gradio Compatibility
async def ingest_document(file: UploadFile):
    global vectorstore, embedding_function
    if not vectorstore:
        initialize_rag()
    
    # Clean filename
    clean_name = os.path.basename(file.filename)
    temp_filename = f"temp_{uuid4()}_{clean_name}"
    
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        if temp_filename.endswith(".pdf"):
            loader = PyPDFLoader(temp_filename)
        else:
            loader = TextLoader(temp_filename)
        
        docs = loader.load()
        
        # Split
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Add metadata for citation
        for doc in splits:
             doc.metadata["source"] = clean_name
        
        # CLEAR CONTEXT: Create a NEW vector store instead of adding to the old one
        print("Creating new vector store (Clearing previous context)...")
        vectorstore = FAISS.from_documents(documents=splits, embedding=embedding_function)
        vectorstore.save_local("faiss_index_local") 
        
        # Re-initialize retriever
        global retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
        
        # IMPORTANT: Rebuild the chain so it uses the NEW retriever!
        create_rag_chain()
        
        return {"message": "Document processed", "chunks": len(splits)}
    except Exception as e:
        print(f"Ingest Error: {e}")
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

async def ask_question(question: str):
    global rag_chain, vectorstore
    if not rag_chain:
        initialize_rag()
    
    if not rag_chain:
        return "System initializing or API Key missing. Please wait."

    try:
        response = rag_chain.invoke(question)
        return response
    except Exception as e:
        return f"Error: {e}"

async def clear_database():
    global vectorstore, retriever, rag_chain, embedding_function
    if not embedding_function:
         initialize_rag() # Re-init if needed
         
    vectorstore = FAISS.from_texts(["Start fresh."], embedding_function)
    vectorstore.save_local("faiss_index_local")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # Rebuild Chain
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
    template = """You are a helpful Study Assistant.
Answer the question based ONLY on the following context.
If the answer is not in the context, say "I couldn't find that in your notes."

Context:
{context}

Question:
{question}

Answer:
"""
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(f"{doc.page_content}\n(Source: {doc.metadata.get('source', 'Unknown')})" for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return {"message": "Database cleared"}

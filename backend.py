from google import genai
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ✅ Configure Gemini using environment variable securely
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def process_pdf(file_path):
    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        print(f"\n[ERROR] File not found: {abs_path}")
        return None

    loader = PyPDFLoader(abs_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    return text_splitter.split_documents(documents)


def ask_question(vector_db, query):
    docs = vector_db.similarity_search(query, k=3)
    context = " ".join([doc.page_content for doc in docs])

    prompt = f"""
Answer the question ONLY based on the context provided below. Do not hallucinate or use outside information.
Provide a clear and detailed explanation in exactly 4-5 sentences.

Context:
{context}

Question:
{query}

Answer:
"""
    
    # Initialize Gemini model and generate the answer
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text
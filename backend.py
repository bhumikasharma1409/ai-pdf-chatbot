import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline

# ✅ Generative model
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

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
Answer the question based on the context below.

Context:
{context}

Question:
{query}

Answer in a complete and clear sentence:
"""

    result = generator(prompt, max_length=200)

    return result[0]["generated_text"]
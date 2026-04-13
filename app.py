import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline


qa_pipeline = pipeline(
    "question-answering",
    model="distilbert-base-cased-distilled-squad"
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

    result = qa_pipeline(
        question=query,
        context=context
    )

    return result["answer"]


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_pdf = os.path.join(base_dir, "data", "sample.pdf")

    chunks = process_pdf(target_pdf)

    if chunks:
        print(f"✅ Created {len(chunks)} chunks")

        print("⚡ Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2"
        )

        vector_db = FAISS.from_documents(chunks, embeddings)
        print("✅ Vector DB ready!\n")

        print("--------------------------------------------------")

        while True:
            query = input("Ask a question (or 'q' to quit): ")

            if query.lower() in ['q', 'quit', 'exit']:
                print("Goodbye!")
                break

            if not query.strip():
                continue

            print("\n🤖 Thinking...")
            answer = ask_question(vector_db, query)

            print("\n📌 Answer:\n", answer)
            print("\n--------------------------------------------------")
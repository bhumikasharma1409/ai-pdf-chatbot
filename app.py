import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- NEW IMPORTS ---
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFaceHub

def process_pdf(file_path):
    # Cross-platform safe absolute path
    abs_path = os.path.abspath(file_path)
    
    # Custom Error Handling: check if file actually exists
    if not os.path.exists(abs_path):
        print(f"\n[ERROR] File not found!")
        print(f"System looked for your PDF here: {abs_path}")
        print("Please ensure the 'data' folder exists and 'sample.pdf' is placed inside it.")
        return None

    loader = PyPDFLoader(abs_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    return chunks

def ask_question(vector_db, query, llm_choice="huggingface"):
    """
    Retrieves context from FAISS and generates an answer using an LLM.
    """
    # 1. Initialize the chosen Language Model
    if llm_choice == "openai":
        # Requires OPENAI_API_KEY set as an environment variable
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    else:
        # Requires HUGGINGFACEHUB_API_TOKEN set as an environment variable
        # We use mistralai/Mistral-7B-Instruct-v0.2 as a strong free default
        llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            model_kwargs={"temperature": 0.1, "max_new_tokens": 512}
        )

    # 2. Setup the Retriever (fetch top 3 most relevant chunks)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    # 3. Create the Prompt Template
    prompt_template = """You are a helpful assistant. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.

Context: {context}
Question: {input}

Answer:"""
    prompt = PromptTemplate.from_template(prompt_template)

    # 4. Create the Chains
    # This chain handles passing the retrieved text to our LLM along with the prompt
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    # This chain handles actually fetching the relevant documents from FAISS
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 5. Invoke the chain to get the answer
    response = rag_chain.invoke({"input": query})
    return response["answer"]


if __name__ == "__main__":
    # OS-safe path joining. __file__ gets the directory of the current script.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_pdf = os.path.join(base_dir, "data", "sample.pdf")
    
    chunks = process_pdf(target_pdf)
    if chunks is not None:
        print(f"Successfully created {len(chunks)} chunks.")
        
        # --- NEW LOGIC: Embeddings & DB Creation ---
        print("Generating embeddings and building Vector Database...")
        # all-MiniLM-L6-v2 is a great fast/free local embedding model
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
        vector_db = FAISS.from_documents(chunks, embeddings)
        print("Vector Database is ready!\n")
        print("--------------------------------------------------")
        
        # Interactive CLI Loop
        while True:
            try:
                user_query = input("Ask a question about the PDF (or 'q' to quit): ")
                if user_query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                if not user_query.strip():
                    continue
                    
                print("\nThinking...")
                # To use OpenAI, change this to: llm_choice="openai"
                answer = ask_question(vector_db, user_query, llm_choice="huggingface")
                print(f"Answer: {answer}\n")
                print("--------------------------------------------------")
            except Exception as e:
                print(f"\n[ERROR] Something went wrong: {e}\n")
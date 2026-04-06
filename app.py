from langchain_community.document_loaders import PyPDFLoader

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


if __name__ == "__main__":
    chunks = process_pdf("data/sample.pdf")
    print(len(chunks))
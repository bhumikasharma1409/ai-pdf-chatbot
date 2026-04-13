from backend import process_pdf, ask_question
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import gradio as gr

def handle_process_pdf(file_path):
    if not file_path:
        return None, "⚠️ Please upload a PDF first."
    
    chunks = process_pdf(file_path)
    if not chunks:
        return None, "❌ Failed to process PDF."

    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2"
        )
        vector_db = FAISS.from_documents(chunks, embeddings)
        return vector_db, f"✅ PDF processed successfully! ({len(chunks)} chunks created)"
    except Exception as e:
        return None, f"❌ Error creating vector DB: {str(e)}"

def handle_ask_question(vector_db, query):
    if not vector_db:
        return "⚠️ Please process a PDF first before asking questions."
    if not query.strip():
        return "⚠️ Please enter a question."
    
    try:
        answer = ask_question(vector_db, query)
        return answer
    except Exception as e:
        return f"❌ Error answering question: {str(e)}"

# Gradio Blocks UI
with gr.Blocks(title="AI PDF Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("<center><h1>📄 AI PDF Chatbot</h1></center>")
    gr.Markdown("<center>Upload a PDF document, process it, and ask questions! Powered by LangChain and HuggingFace.</center>")
    
    # State to preserve the vector database between events
    vector_db_state = gr.State()
    
    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            process_btn = gr.Button("⚙️ Process PDF", variant="primary")
            status_text = gr.Textbox(label="Status", interactive=False)
            
        with gr.Column(scale=2):
            question_input = gr.Textbox(label="Ask a Question", placeholder="Type your question here...")
            ask_btn = gr.Button("💬 Ask Question", variant="primary")
            answer_output = gr.Textbox(label="Answer", interactive=False, lines=6)
            
    # Connect UI elements to functions
    process_btn.click(
        fn=handle_process_pdf,
        inputs=[pdf_input],
        outputs=[vector_db_state, status_text],
        show_progress=True
    )
    
    ask_btn.click(
        fn=handle_ask_question,
        inputs=[vector_db_state, question_input],
        outputs=[answer_output],
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch()
import gradio as gr
import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def upload_pdf(file):
    if file is None:
        return "Please select a PDF."

    with open(file.name, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload",
            files={
                "file": (
                    file.name.split("/")[-1],
                    f,
                    "application/pdf"
                )
            }
        )
    if response.status_code != 200:
        return "Upload failed."
    
    data = response.json()

    return (
        f"✅ {data['message']}\n"
        f"Filename: {data['filename']}\n"
        f"Chunks Stored: {data['chunks_stored']}"
    )

def ask_question(question):
    if not question.strip():
        return "Please enter a question."

    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": question
        }
    )

    if response.status_code != 200:
        return "Failed to get answer."

    data = response.json()

    return data["answer"]

with gr.Blocks(title="KnowledgeHub AI") as demo:

    gr.Markdown("# KnowledgeHub AI")

    gr.Markdown("""
# 📚 KnowledgeHub AI

### Intelligent Document Question Answering System

Upload a PDF document and ask questions based on its contents using Retrieval-Augmented Generation (RAG).
""")

    pdf = gr.File(label="Upload PDF")

    upload_btn = gr.Button("Upload")

    upload_output = gr.Textbox(
        label="Upload Status",
        interactive=False
    )

    gr.Markdown("---")

    question = gr.Textbox(
        label="Ask a Question",
        placeholder="Type your question..."
    )

    ask_btn = gr.Button("Ask")

    answer = gr.Textbox(
        label="Answer",
        lines=12,
        interactive=False
    )

    upload_btn.click(
        upload_pdf,
        inputs=pdf,
        outputs=upload_output
    )

    ask_btn.click(
        ask_question,
        inputs=question,
        outputs=answer
    )

demo.launch()
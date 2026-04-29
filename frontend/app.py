import gradio as gr
import requests

API_URL = "http://localhost:8000/api"


def upload_pdf(file):
    if file is None:
        return "Nenhum arquivo selecionado."

    with open(file, "rb") as f:
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": (file, f, "application/pdf")}
        )

    if response.status_code == 200:
        return f"✅ {response.json()['filename']} indexado com sucesso"
    else:
        return f"❌ Erro: {response.json().get('detail', 'Erro desconhecido')}"


def chat(pergunta, historico):
    history_formatted = []
    for humano, assistente in historico:
        history_formatted.append({"role": "user", "content": humano})
        history_formatted.append({"role": "assistant", "content": assistente})

    response = requests.post(
        f"{API_URL}/chat",
        json={
            "question": pergunta,
            "history": history_formatted
        }
    )

    if response.status_code == 200:
        return response.json()["answer"]
    else:
        return f"❌ Erro: {response.json().get('detail', 'Erro desconhecido')}"


with gr.Blocks(title="Chat com PDF", theme=gr.themes.Soft()) as app:

    gr.Markdown("# 📄 Chat com PDF")

    with gr.Tab("📤 Upload"):
        pdf_input = gr.File(label="Selecione um PDF", file_types=[".pdf"])
        upload_btn = gr.Button("Enviar PDF", variant="primary")
        upload_status = gr.Textbox(label="Status", interactive=False)

        upload_btn.click(
            fn=upload_pdf,
            inputs=pdf_input,
            outputs=upload_status
        )

    with gr.Tab("💬 Chat"):
        gr.ChatInterface(fn=chat)

if __name__ == "__main__":
    app.launch()
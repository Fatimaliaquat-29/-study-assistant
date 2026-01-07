import gradio as gr
import asyncio
from backend import rag
from backend import analysis

# Initialize Backend
rag.initialize_rag()

async def chat_function(message, history):
    return await rag.ask_question(message)

async def upload_files(files):
    if not files:
        return "No files uploaded."
    
    results = []
    # For now, just process the first file to match "Clear Context" logic, 
    # or loop through. The backend logic currently clears DB on each call, 
    # so we should only pass one file or modify backend to add.
    # Given user wants "Start Fresh", we process the *last* file effectively for now
    # or process one.
    
    # Let's process the first one for simplicity as per current logic
    # or iterate. But backend clears DB every time! 
    # So we should call it once.
    
    # Actually, Gradio likely passes a list of paths.
    # We will pick the last one to be the "Active" context.
    
    file_path = files[0] # Just take one
    if isinstance(files, list):
         file_path = files[0].name if hasattr(files[0], 'name') else files[0]

    result = await rag.ingest_document(file_path)
    return f"Processed {os.path.basename(file_path)}: {result}"

async def analyze_text(text):
    result = await analysis.analyze_text(text)
    return str(result) # Return JSON string for now or format it pretty

# Custom Theme (Matcha Latte-ish)
theme = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="stone",
).set(
    body_background_fill="#FDFBF7", # Latte
    block_background_fill="#FFFFFF",
    button_primary_background_fill="#A8C69F", # Sage
    button_primary_text_color="#FFFFFF"
)

with gr.Blocks(theme=theme, title="Study Assistant") as demo:
    gr.Markdown("# 🍵 Study Assistant")
    
    with gr.Tab("💬 Study Chat"):
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(label="Upload Notes (PDF/TXT)", file_count="single")
                upload_status = gr.Textbox(label="Status", interactive=False)
                file_input.upload(upload_files, file_input, upload_status)
                
            with gr.Column(scale=4):
                chatbot = gr.ChatInterface(
                    fn=chat_function, 
                    description="Upload your notes and ask questions!",
                    examples=["Summarize this document", "What are the key dates?"]
                )

    with gr.Tab("📝 Analysis Tools"):
        with gr.Row():
            txt_input = gr.Textbox(label="Input Text", lines=10, placeholder="Paste essay here...")
            analyze_btn = gr.Button("Analyze", variant="primary")
        
        json_output = gr.JSON(label="Analysis Result")
        analyze_btn.click(analyze_text, inputs=[txt_input], outputs=[json_output])

if __name__ == "__main__":
    demo.launch()

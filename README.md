# 🎓 AI Student Study Assistant

A powerful, aesthetic, and privacy-focused study companion built with **FastAPI**, **LangChain**, and **Groq**.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## ✨ Features

-   **📚 Chat with Notes (RAG)**: Upload PDF/TXT lecture notes and ask questions.
    -   *Powered by Local Embeddings (HuggingFace) - No API costs for storage.*
    -   *Cites sources (e.g., "Source: lecture1.pdf").*
-   **⚡ Ultra-Fast AI**: Uses **Groq (Llama 3)** for near-instant responses.
-   **📝 Analysis Tools**:
    -   **Grammar Checker**: Fixes essays instantly.
    -   **AI Detector**: Estimates if text was written by AI.
-   **🎨 Aesthetic UI**: "Matcha Latte" & "Scrapbook" theme with a fully responsive design.
-   **🔒 Secure Auth**: User registration and login protected by JWT.

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, Uvicorn
-   **AI/LLM**: LangChain, Groq API (Llama 3), HuggingFace Embeddings (SentenceTransformers)
-   **Vector DB**: FAISS (Local)
-   **Frontend**: Vanilla HTML/CSS/JS (Lightweight & Fast)
-   **Auth**: Supabase (Backend Logic) / Local SQLite (Dev)

## 🚀 Getting Started

### Prerequisites
-   Python 3.9+
-   A [Groq API Key](https://console.groq.com) (Free)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/study-assistant.git
    cd study-assistant
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Setup Environment:**
    Create a `.env` file in the root directory:
    ```ini
    GROQ_API_KEY=gsk_...your_key_here...
    SECRET_KEY=your_secret_key
    ```

5.  **Run the App:**
    ```bash
    .\run.bat
    # OR
    uvicorn backend.main:app --reload
    ```

6.  Open **http://localhost:8000** in your browser.

## 📂 Project Structure

```
├── backend/
│   ├── main.py       # FastAPI Entry point
│   ├── rag.py        # RAG (Retrieval Augmented Generation) Logic
│   ├── analysis.py   # AI Analysis Tools
│   └── auth.py       # Authentication Handles
├── frontend/
│   ├── index.html    # Main Dashboard
│   ├── style.css     # "Matcha Latte" Theme
│   └── script.js     # Frontend Logic
└── requirements.txt  # Python Dependencies
```

## 🛡️ License

This project is open-source and available under the [MIT License](LICENSE).

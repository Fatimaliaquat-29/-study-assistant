# 🚀 How to Deploy Your App (Share with a Link)

Currently, your app runs on your computer (`localhost`). To let others use it, you need to put it on the cloud.

The easiest (and free) way for this Python app is **Render**.

## Step 1: Push to GitHub
1.  Go to [GitHub.com](https://github.com) and create a new repository called `study-assistant`.
2.  Open your terminal in VS Code and run:
    ```bash
    git init
    git add .
    git commit -m "Ready for deploy"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/study-assistant.git
    git push -u origin main
    ```

## Step 2: Deploy on Render
1.  Go to [Render.com](https://render.com) and Sign Up (you can use GitHub).
2.  Click **"New +"** -> **"Web Service"**.
3.  Connect your GitHub repository.
4.  **Settings**:
    -   **Name**: `my-study-app` (or whatever you want)
    -   **Runtime**: `Python 3`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables** (Important!):
    -   Add `GROQ_API_KEY`: Paste your key `gsk_...`
    -   Add `SECRET_KEY`: `randomstring123`
6.  Click **Create Web Service**.

## Step 3: Done!
Render will give you a link like `https://my-study-app.onrender.com`.
You can send this link to anyone!

---

### ⚠️ Note on Database
Since we are using a local file database (`users.db` / SQLite), your data *might* reset if Render restarts the server.
*   **For permanent data**: You would need to connect a real PostgreSQL database (Supabase/Render Postgres), but for a portfolio demo, the current setup is fine!

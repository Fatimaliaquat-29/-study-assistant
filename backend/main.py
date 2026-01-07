from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from backend.rag import ingest_document, ask_question, clear_database
import backend.auth as auth
import backend.analysis as analysis
from datetime import timedelta
import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Student Study Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class ChatRequest(BaseModel):
    question: str

class AnalysisRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')

# --- Authentication Endpoints ---

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: auth.UserCreate):
    success, message = auth.create_user(user)
    print(f"DEBUG: success={success}, message={message}") 
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "User registered successfully"}

@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.get_user(form_data.username)
    if not user or not auth.verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected Endpoints ---

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: auth.User = Depends(auth.get_current_user)):
    try:
        return await ingest_document(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest, current_user: auth.User = Depends(auth.get_current_user)):
    try:
        if not os.environ.get("GROQ_API_KEY"):
             raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in .env")
        
        answer = await ask_question(request.question)
        return {"answer": answer}
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear(current_user: auth.User = Depends(auth.get_current_user)):
    return await clear_database()

@app.post("/analyze")
async def analyze(request: AnalysisRequest, current_user: auth.User = Depends(auth.get_current_user)):
    try:
        if not os.environ.get("GROQ_API_KEY"):
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not found")
            
        result = await analysis.analyze_text(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

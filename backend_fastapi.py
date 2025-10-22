# backend_fastapi.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="GoodKarma Chatbot API")

# Allow CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Questions ===
triage_questions = {
    1: "Do you sometimes feel like you’re navigating a world that doesn’t always match how you think or feel—especially with social rules, routines, or sensory overload?",
    2: "Do your moods or worries sometimes shift suddenly or feel too intense?",
    3: "Do you ever feel disconnected from reality, unsure of who you are, or like your thoughts and experiences aren’t always grounded?",
    4: "Do you sometimes feel like your urges or habits take over—food, sleep, substances, or acting impulsively?",
    5: "Are you feeling confused or frustrated with your body, gender, or sexual health?",
    6: "Would you like to explore if your personality patterns might be affecting your wellbeing?"
}

# === In-memory store for simplicity ===
sessions = {}

# === Request Models ===
class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str

class StartSessionRequest(BaseModel):
    session_id: str
    name: str
    age: int
    gender: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    known_illnesses: Optional[str] = None
    active_medicines: Optional[str] = None

# === Start a new session ===
@app.post("/start-session")
def start_session(req: StartSessionRequest):
    if req.session_id in sessions:
        raise HTTPException(status_code=400, detail="Session already exists")
    
    sessions[req.session_id] = {
        "user_info": req.dict(),
        "question_index": 0,
        "answers": []
    }

    # Return first question
    first_question = {
        "id": 1,
        "text": triage_questions[1],
        "options": ["Yes", "No"]
    }
    return {"nextQuestion": first_question}

# === Submit answer and get next question ===
@app.post("/submit-answer")
def submit_answer(req: AnswerRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[req.session_id]
    session["answers"].append({"question_id": req.question_id, "answer": req.answer})
    session["question_index"] += 1

    if session["question_index"] >= len(triage_questions):
        return {"nextQuestion": None, "message": "All questions completed!"}

    next_q_id = session["question_index"] + 1
    next_question = {
        "id": next_q_id,
        "text": triage_questions[next_q_id],
        "options": ["Yes", "No"]
    }
    return {"nextQuestion": next_question}

# === Reset session for testing ===
@app.post("/reset-session/{session_id}")
def reset_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "reset"}

# === Get session answers (for testing) ===
@app.get("/get-answers/{session_id}")
def get_answers(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"answers": sessions[session_id]["answers"]}

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="HardLaunch")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    summary: Optional[dict] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    import uuid
    
    if not request.session_id or request.session_id not in sessions:
        session_id = request.session_id or str(uuid.uuid4())
        sessions[session_id] = {
            "messages": [],
            "summary": None,
            "survey_complete": False
        }
    else:
        session_id = request.session_id
    
    session = sessions[session_id]
    session["messages"].append({"role": "user", "content": request.message})
    
    if not session["survey_complete"]:
        response_text = generate_survey_response(session, request.message)
    else:
        response_text = generate_agent_response(session, request.message)
    
    session["messages"].append({"role": "assistant", "content": response_text})
    
    return ChatResponse(
        session_id=session_id,
        response=response_text,
        summary=session.get("summary")
    )

def generate_survey_response(session, user_message):
    messages = session["messages"]
    user_messages_count = len([m for m in messages if m["role"] == "user"])
    
    if user_messages_count == 1:
        return "Welcome to HardLaunch! Let's build your startup together. To get started, tell me about your business idea. What problem are you solving?"
    elif user_messages_count == 2:
        return "Great idea! Who is your target audience or customer? Who will benefit most from your solution?"
    elif user_messages_count == 3:
        return "Excellent! What makes your solution unique? What's your competitive advantage or 'moat'?"
    elif user_messages_count == 4:
        return "Perfect! What are your main constraints or limitations? (e.g., budget, time, resources, regulations)"
    else:
        session["survey_complete"] = True
        session["summary"] = {
            "idea": messages[0]["content"] if len(messages) > 0 else "Not provided",
            "target_audience": messages[2]["content"] if len(messages) > 2 else "Not provided",
            "competitive_advantage": messages[4]["content"] if len(messages) > 4 else "Not provided",
            "constraints": messages[6]["content"] if len(messages) > 6 else "Not provided",
            "status": "Survey completed"
        }
        return f"Thank you for completing the survey! I now understand your business:\n\n" \
               f"✓ Your idea and the problem you're solving\n" \
               f"✓ Your target audience\n" \
               f"✓ Your competitive advantage\n" \
               f"✓ Your constraints\n\n" \
               f"You can now navigate to the Dashboard to explore different agents that will help you with " \
               f"Business Planning, Financial Research, Market Analytics, and Engineering & Development. " \
               f"Each agent is specialized to help you in different areas of your startup journey!"

def generate_agent_response(session, user_message):
    message_lower = user_message.lower()
    
    if "business" in message_lower:
        return "Business Planning Agent: I can help you with:\n" \
               "• Refining your business idea and value proposition\n" \
               "• Identifying your target users and market segments\n" \
               "• Assessing your startup stage and readiness\n" \
               "• Analyzing risks and creating mitigation strategies\n" \
               "• Planning your growth trajectory\n\n" \
               "What specific area would you like to focus on?"
    
    elif "finance" in message_lower or "financial" in message_lower:
        return "Financial Research Agent: I can help you with:\n" \
               "• Budget estimation and financial planning\n" \
               "• Sales targets and revenue projections\n" \
               "• Pricing model optimization\n" \
               "• Funding strategies and investor preparation\n" \
               "• Physical asset planning\n" \
               "• Financial security and risk management\n\n" \
               "What financial aspect do you need guidance on?"
    
    elif "market" in message_lower:
        return "Market Analytics Agent: I can help you with:\n" \
               "• Market size and opportunity analysis\n" \
               "• Location and expansion strategies\n" \
               "• Competitor research and positioning\n" \
               "• Success rate benchmarking\n" \
               "• Marketing and Go-To-Market (GTM) strategies\n\n" \
               "Which market analysis would be most valuable for you?"
    
    elif "engineering" in message_lower or "technical" in message_lower:
        return "Engineering & Development Agent: I can help you with:\n" \
               "• Technology stack recommendations\n" \
               "• Software architecture design\n" \
               "• Machine learning integration opportunities\n" \
               "• Third-party integrations and APIs\n" \
               "• Development roadmap planning\n\n" \
               "What technical challenge can I help you with?"
    
    else:
        return "I'm here to help with your startup! You can ask me about:\n" \
               "• Business planning and strategy\n" \
               "• Financial projections and funding\n" \
               "• Market analysis and competition\n" \
               "• Engineering and technical development\n\n" \
               "Visit the Dashboard to access specialized agents, or tell me what you'd like to explore!"

@app.get("/")
async def root():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

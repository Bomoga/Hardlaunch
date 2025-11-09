# HardLaunch - AI Startup Planning Assistant

## Overview

HardLaunch is an AI-powered startup planning platform that helps entrepreneurs transform business ideas into actionable strategies. The system uses an agentic workflow architecture built on Google's ADK (Agent Development Kit) to conduct conversational intake sessions and generate comprehensive business plans across multiple dimensions including business strategy, finance, market analysis, and engineering.

The platform guides users through a structured survey process to capture their startup vision, then leverages specialized AI agents to provide expert guidance on business planning, funding strategy, market analysis, and technical architecture.

**Current Status:** Fully functional with Google ADK agents integrated. The frontend is connected to the backend, and the survey/agent system is operational. RAG system is temporarily simplified to improve startup time.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Web-based Static Site**
- Pure HTML/CSS/JavaScript implementation without a framework
- Multiple page structure: Home (chat interface), Dashboard (summary view), Agents (capability overview), Reports (export/edit)
- Custom CSS with space-themed design (stars background, dark navy palette)
- Client-side state management using localStorage for session persistence
- Session ID tracking to maintain conversation context across page navigation

**Key Design Patterns:**
- No build step required - direct file serving
- Responsive layouts using CSS flexbox/grid
- RESTful API communication via fetch API
- Progressive disclosure of business summary information

### Backend Architecture

**FastAPI Server (Primary)**
- Modern Python async web framework serving as the main API gateway
- CORS middleware configured for cross-origin requests
- Session management using in-memory dictionary (sessions object)
- Chat endpoint (`/api/chat`) orchestrates the agent workflow
- Static file serving for frontend assets

**Agent Orchestration (Google ADK)**
- Sequential agent workflow combining survey intake with specialized planning agents
- Onboarding agent coordinates survey_agent → context_manager_agent flow
- Context manager serves as central hub, routing to specialized agents:
  - Business Planning Agent ("Armstrong") - business model, strategy, risk assessment
  - Funding Research Agent ("Aldrin") - financial planning, pricing, funding sources
  - Market Analysis Agent ("Gagarin") - competitive analysis, market sizing, GTM strategy
  - Engineering Agent ("Collins") - tech stack recommendations, architecture design

**State Management:**
- InMemorySessionService for session persistence during runtime
- User-scoped state storage via ADK's State system
- Business summary stored with metadata (source, timestamp) in `BUSINESS_SUMMARY_KEY`

**RAG System (Active - Hybrid Approach)**
- Combines two knowledge sources for maximum accuracy:
  1. **In-memory startup fundamentals**: Business models, funding stages, market sizing (TAM/SAM/SOM), tech stacks, GTM strategies, pricing frameworks
  2. **LlamaIndex vector store**: "Hacking Growth" by Sean Ellis - 8 documents on growth hacking, lean experiments, user acquisition, onboarding, scaling
- Semantic keyword matching retrieves relevant content from both sources
- Queries enriched with user's business summary for personalized guidance
- Provides grounded evidence from curated frameworks + growth hacking tactics
- Graceful fallback if vector store unavailable (uses in-memory knowledge)
- Optimized for comprehensive, accurate startup guidance

**AI Models:**
- Primary reasoning: Gemini 2.5 Flash (fast, cost-effective)
- Embeddings: Google models/embedding-001
- All agents use consistent Gemini 2.5 Flash model for coherent reasoning

### Data Flow

1. **User Input** → Frontend chat interface
2. **Session Check** → Backend validates/creates session ID
3. **Survey Phase** → Survey agent collects business information progressively
4. **Summary Generation** → Business summary saved to user state
5. **Context Routing** → Context manager agent directs to specialized agents
6. **RAG Enhancement** → Queries enriched with business context and external knowledge
7. **Response Delivery** → Structured responses returned to frontend
8. **State Persistence** → Session and summary data maintained across interactions

### Security Considerations

**Flask App Security Features (src/app.py):**
- JWT-based authentication with configurable expiration
- Bcrypt password hashing for user credentials
- Flask-Talisman for security headers (CSP, HTTPS enforcement)
- Flask-Limiter for rate limiting (5 reg/min, 10 login/min)
- In-memory user storage (temporary demo implementation)

**Production Concerns:**
- Current implementation uses in-memory storage (ephemeral)
- JWT secret key hardcoded (needs environment variable)
- CORS set to allow all origins (needs restriction)
- No database persistence (sessions lost on restart)

### Tool System

**Context Memory Tools:**
- `save_business_summary()` - Persists business summary with source tracking
- `get_business_summary()` - Retrieves current business context
- Normalization and validation of summary data
- Timestamp tracking for update history

**RAG Tools:**
- `rag_lookup()` - Fetches grounded evidence from document store
- Query enrichment with business summary context
- Configurable top_k retrieval (default: 5 documents)
- Integration with LlamaIndex query engine

**Web Search:**
- Google search integration via ADK's google_search tool
- Used by specialized agents for real-time market research

## External Dependencies

### AI/ML Services
- **Google Gemini API** - Primary LLM for all agent reasoning and embeddings
- **Google ADK** - Agent framework, session management, tool orchestration
- **LlamaIndex** - Vector database and document indexing framework

### Python Frameworks
- **FastAPI** - Modern async web framework for REST API
- **Flask** - Alternative web framework (appears in security module)
- **Uvicorn** - ASGI server for FastAPI deployment

### Security & Authentication
- **Flask-JWT-Extended** - JWT token management
- **Flask-Bcrypt** - Password hashing
- **Flask-Talisman** - Security headers and HTTPS enforcement
- **Flask-Limiter** - Rate limiting protection

### Machine Learning & Data
- **PyTorch** - Deep learning framework (for embeddings/models)
- **Sentence-Transformers** - Semantic similarity and embeddings
- **FAISS** - Facebook AI Similarity Search for vector operations
- **Scikit-learn** - Machine learning utilities
- **NumPy/Pandas** - Data manipulation and analysis

### Content Processing
- **BeautifulSoup4** - Web scraping and HTML parsing
- **PyPDF** - PDF document extraction
- **yt-dlp** - YouTube video download
- **youtube-transcript-api** - YouTube caption extraction
- **OpenAI Whisper** - Audio transcription (for video content)

### Utilities
- **python-dotenv** - Environment variable management
- **Pydantic** - Data validation and settings management
- **HTTPX** - Async HTTP client
- **Requests** - Synchronous HTTP client

### Configuration Requirements
- **GEMINI_API_KEY** - Required environment variable for Google AI access (configured in Replit Secrets)
- **API_PROVIDER** - Optional, defaults to "google"
- **MODEL_NAME** - Optional, defaults to "gemini-2.5-flash"
- **EMBED_MODEL_NAME** - Optional, defaults to "models/embedding-001"

### Deployment Setup
- **Server**: FastAPI/Uvicorn on port 5000
- **Hosting**: 0.0.0.0 (allows proxy access)
- **Workflow**: Configured for autoscale deployment
- **Static Files**: Served from /static directory
- **API Endpoint**: /api/chat for agent interactions

### Known Architectural Limitations
- Session storage is in-memory only (not production-ready)
- No database integration despite having multiple database libraries
- Multiple requirements files with some redundancy (requirement.txt vs requirements.txt vs requirements_consolidated.txt)
- Frontend/backend deployed separately (static site at GitHub Pages, backend unclear)
- JWT secret key and security configurations hardcoded
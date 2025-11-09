# HardLaunch

SharkByte 2025

## Description & Features

HardLaunch runs an agentic workflow that converts ideas into an actionable strategy. A conversational intake captures the problem, audience, solution, moat, and constraints, while a context manager maintains a live summary of the venture that persists across interactions. Specialized planning, finance, and market agents then generate focused analyses and recommendations. A retrieval-augmented generation layer draws from uploaded research to surface evidence and citations. All results appear in a navigable founder dashboard where you refine strategy, inspect sources, and seamlessly hand off tasks to the appropriate agent.

## Technologies

The system is implemented with Google’s ADK agent framework, using Gemini 2.5 Flash for reasoning and models/embedding-001 for vector search. Documents are stored in a LlamaIndex vector database persisted under src/data/persist, with Whisper/YouTube ingestion hooks to handle rich media. A FastAPI backend exposes an /api/chat endpoint for the UI, and the ADK session service shares state so onboarding, context management, and tool calls remain synchronized.

## Setup

Site is live at https://bomoga.github.io/Hardlaunch/

## Contributors

Adrian Morton - Backend/ML/AI Engineer

Khanh Truong - Backend/ML/AI Engineer

Francesca Dumary - Frontend/Web/Software Engineer

Matthew Manzitti - Cyber/Security Engineer

## Demo Video

## Screenshots

<img width="252.25" height="179.5" alt="Screenshot 2025-11-08 153930" src="https://github.com/user-attachments/assets/37326327-ba6b-41a3-a240-3cacf602c3b8" />

<img width="252.25" height="179.5" alt="Screenshot 2025-11-08 164403" src="https://github.com/user-attachments/assets/34bf963f-55ee-45a3-bcf0-432302663580" />

<img width="252.25" height="179.5" alt="Screenshot 2025-11-08 172855" src="https://github.com/user-attachments/assets/6164640c-c74b-494a-b3b3-0a3ddc21c46a" />

<img width="252.25" height="179.5" alt="Screenshot 2025-11-08 182150" src="https://github.com/user-attachments/assets/97fb6684-c61d-48d4-88d4-e798b8f19601" />

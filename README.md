# HardLaunch

<img width="203" height="203" alt="content" src="https://github.com/user-attachments/assets/c7530833-b461-4780-9ca8-97d96dae51d0" />

SharkByte 2025

## Description & Features

HardLaunch runs an agentic workflow that converts ideas into an actionable strategy. A conversational intake captures the problem, audience, solution, moat, and constraints, while a context manager maintains a live summary of the venture that persists across interactions. Specialized planning, finance, and market agents then generate focused analyses and recommendations. A retrieval-augmented generation layer draws from uploaded research to surface evidence and citations. All results are displayed in a navigable founder dashboard, where you can refine your strategy, inspect sources, and seamlessly hand off tasks to the appropriate agent.

## Technologies

The system is implemented with Google’s ADK agent framework, using Gemini 2.5 Flash for reasoning and models/embedding-001 for vector search. Documents are stored in a LlamaIndex vector database persisted under src/data/persist, with Whisper/YouTube ingestion hooks to handle rich media. A FastAPI backend exposes an /api/chat endpoint for the UI, and the ADK session service shares state, so onboarding, context management, and tool calls remain synchronized.

## Setup

Site is live at https://bomoga.github.io/Hardlaunch/

## Contributors

Adrian Morton - Backend/ML/AI Engineer

Khanh Truong - Backend/ML/AI Engineer

Francesca Dumary - Frontend/Web/Software Engineer

Matthew Manzitti - Cyber/Security Engineer

## Demo Video

## Screenshots

<img width="203" height="144.6" alt="Screenshot 2025-11-09 011909" src="https://github.com/user-attachments/assets/6e98b71f-a125-4900-af68-c7022bcb1d89" />

<img width="203" height="144.6" alt="Screenshot 2025-11-09 023635" src="https://github.com/user-attachments/assets/bb4ffa9c-2f91-4f93-b132-f2d16e3d8633" />

<img width="203" height="144.6" alt="Screenshot 2025-11-09 023613" src="https://github.com/user-attachments/assets/77d9d603-06af-4860-856b-a102320b943f" />

<img width="203" height="144.6" alt="Screenshot 2025-11-09 023658" src="https://github.com/user-attachments/assets/f0cd199d-dc84-4428-bb25-2f6de0ef77a6" />

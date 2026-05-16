# ServisAI - AI Service Orchestrator

ServisAI is an AI-powered service orchestrator designed for Pakistan's informal service economy. It converts noisy, multilingual user requests into a complete service lifecycle, including intent understanding, provider discovery, ranking, pricing, booking simulation, and feedback handling.

## Project Structure

- `backend/`: FastAPI backend containing the agentic workflow.
  - `agents/`: AI agents for Intent and Discovery.
  - `services/`: Business logic and agent runners.
  - `utils/`: Utility functions for maps, tracing, and data handling.
  - `tools/`: Specialized tools for map interactions.

## Features

- **Intent Agent**: Parses Urdu, Roman Urdu, English, and mixed language inputs to extract service requirements.
- **Discovery Agent**: Finds nearby service providers using Google Maps and fallback mock data.
- **Trace Logs**: Every step produces detailed logs for debugging and decision rationale.

## Setup

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt` (Note: Ensure `google-adk`, `fastapi`, `uvicorn`, etc., are installed).
3. Set up environment variables in a `.env` file (see `.env.sample` if available).
4. Run the backend: `cd backend && uvicorn main:app --reload`

## License

MIT

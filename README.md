# ServisAI - AI Service Orchestrator

ServisAI is an AI-powered service orchestrator designed for Pakistan's informal service economy. It converts noisy, multilingual user requests into a complete service lifecycle, including intent understanding, provider discovery, ranking, pricing, booking simulation, and feedback handling.

## Project Structure

The project is structured as a monorepo containing both the backend agentic services and the frontend Flutter application:

- `backend/`: FastAPI Python application handling the AI agentic workflow.
  - `agents/`: AI agents for Intent and Discovery.
  - `services/`: Business logic, orchestrator, and agent runners.
  - `utils/`: Utility functions for maps, tracing, and data handling.
  - `tools/`: Specialized tools for map interactions and service integrations.
- `frontend/`: Flutter application providing the user interface for requests, tracking, and agent traces.
  - `lib/`: Contains the main Dart code for the Flutter application, including screens, widgets, and API service integration.

## Features

### Backend (AI Orchestrator)
- **Intent Agent**: Parses Urdu, Roman Urdu, English, and mixed language inputs to extract service requirements.
- **Discovery Agent**: Finds nearby service providers using Google Maps and fallback mock data.
- **Provider Matching & Pricing**: Calculates matching scores based on distance, rating, budget, complexity, and reputation.
- **Trace Logs**: Every step produces detailed logs for debugging and decision rationale.
- **Fallbacks & Resilience**: Automatically handles API failures, payment rejections, and provider cancellations.

### Frontend (User Interface)
- **Request Screen**: Natural-language input for service requests (e.g., "AC bilkul kaam nahi kar raha kal subah G-13 mein").
- **Agent Trace / Replay Screen**: Visibility into the backend reasoning, showing each trace step as an expandable card (intent reasoning, discovery, pricing, booking execution).
- **Booking & Lifecycle Tracking**: Shows notifications, timeline events, and alternative slot selection for scheduling conflicts.
- **Feedback & Dispute Management**: Post-service feedback submission impacting provider reputation for future matching.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Flutter SDK (stable channel)

### 1. Backend Setup

1. Open a terminal and navigate to the project root.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Navigate to the `backend/` directory: `cd backend`
   - Create a `.env` file containing necessary API keys (e.g., OpenAI, Google Maps).
4. Run the backend server:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
   The backend will be available at `http://127.0.0.1:8000` (check `/api/health` for status).

### 2. Frontend Setup

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install Flutter dependencies:
   ```bash
   flutter pub get
   ```
3. Configure Backend URL:
   - For local development on desktop/web, the app connects to `http://127.0.0.1:8000`.
   - If running on a physical Android/iOS device, ensure the backend URL in the Flutter code is pointed to your machine's local LAN IP address (e.g., `http://192.168.1.10:8000`).
4. Run the Flutter application:
   ```bash
   flutter run
   ```

## License

MIT

# ServisAI - AI Service Orchestrator

ServisAI is an advanced, AI-powered service orchestrator designed for Pakistan's informal service economy. It converts noisy, multilingual user requests (supporting Urdu, Roman Urdu, English, and mixed inputs) into a complete, persistent service lifecycle—spanning intent parsing, location geocoding, provider discovery, multi-factor ranking, deterministic pricing, secure Supabase booking persistence, and lifecycle progress simulation.

---

## Project Structure

- `backend/`: FastAPI backend containing the agentic orchestration workflow.
  - `agents/`: AI agents for Intent, Discovery, Matching, Pricing, and Booking.
  - `orchestration/`: Antigravity/Google ADK sequential control pipeline (`service_pipeline.py`).
  - `services/`: Core logic runners, geocoding, and matchmaking services.
  - `tools/`: Specialized programmatic tools for Maps, Pricing, Booking, and Lifecycle Simulation.
  - `db/`: Database configuration and Supabase client integration (`supabase_client.py`).
  - `utils/`: Structured execution trace logging and utilities.

---

## Key Features & Agents

### 1. Intent Agent
* Parses multilingual inputs (Urdu, Roman Urdu, English, or mixed language) to extract service type, location, datetime preference, urgency, complexity, and budget sensitivity.
* Utilizes a highly resilient dual-LLM structure (Groq LLaMA-3.1 with seamless fallback to Gemini-2.0-flash-lite).
* Detects low confidence and automatically requests user clarification when necessary.

### 2. Discovery Agent
* Translates user sectors/locations into exact latitude/longitude coordinates using the **Google Maps Geocoding API**.
* Discovers nearby service providers using the **Google Maps Places API**.
* Features smart **automatic radius expansion** if insufficient providers are initially found.
* Implements a mock dataset fallback system to guarantee operation even during API limit caps.

### 3. Matching Agent
* Employs a multi-factor weighted ranking algorithm to score candidates.
* Factors in: distance, average rating, total review count, on-time history, specialization matching, cancellation risk, and budget/complexity compatibility.
* Identifies the optimal provider candidate and logs detailed ranking decisions.

### 4. Pricing Agent
* Calculates exact service quotes deterministically using:
  - Base service rate
  - Travel fee (distance-based)
  - Urgency surcharge
  - Complexity multiplier
* Generates a transparent cost breakdown, min/max estimated range, and conversational explanation.

### 5. Booking Agent
* Finalizes execution by creating a persistent service booking object.
* Generates a unique, alphanumeric booking ID (e.g. `SRV-E5B708A9`).
* Calculates a distance-based, deterministic technician arrival ETA.
* Persists the booking immediately to a **Supabase** `bookings` table.

### 6. Booking Lifecycle & Follow-up Simulation
* Deterministically simulates service progression through real-world phases:
  `confirmed` → `technician_assigned` → `on_the_way` → `in_progress` → `completed` → `feedback_requested`.
* Records all lifecycle state updates and technician tracking details into a **Supabase** `booking_events` table for full auditability.

### 7. Central Sequential Orchestration Pipeline
* Runs the entire 6-agent workflow sequentially through the custom **Antigravity / Google ADK-style Sequential Orchestration Pipeline**.
* Centrally propagates a single shared state dictionary across all nodes.
* Appends structured trace logs at every phase to provide comprehensive developer observability and system audits.

---

## API Documentation & Endpoints

### 1. Central Pipeline Execution
* **`POST /api/orchestrate`**: Runs the complete intent-to-booking pipeline in a single call.
  ```bash
  curl -X POST http://127.0.0.1:8000/api/orchestrate \
       -H "Content-Type: application/json" \
       -d '{"message":"AC kharab hai jaldi kisi ko bhejein G-11 mein","user_id":"huzaifa"}'
  ```

### 2. Individual Agent Tests
* **`POST /api/intent`**: Test language parsing and intent extraction.
* **`POST /api/test-discovery`**: Test geocoding and provider discovery.
* **`POST /api/test-matching`**: Test provider discovery and weighted scoring.
* **`POST /api/test-pricing`**: Test service price calculations and breakdowns.

---

## Setup & Running

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **Configure Environment Variables** (in `backend/.env`):
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_MAPS_API_KEY=your_maps_api_key
   GROQ_API_KEY=your_groq_api_key
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```
3. **Launch the Server**:
   ```bash
   uvicorn main:app --reload
   ```

---

## License

MIT

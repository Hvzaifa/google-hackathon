# ServisAI Flutter Developer Backend Integration Guide

## 1. Purpose

This document explains what the Flutter app should implement using the completed ServisAI backend. The backend already handles the agentic workflow:

```txt
User request
→ Intent understanding
→ Provider discovery
→ Provider matching
→ Pricing
→ Scheduling
→ Booking
→ Notifications
→ Lifecycle updates
→ Feedback/dispute
→ Reputation update
→ Fallback/recovery flows
```

The Flutter app’s job is to make this workflow visible, usable, and demo-ready.

---

## 2. Backend base URL

For local development:

```txt
http://127.0.0.1:8000
```

For physical Android/iOS device testing, use the machine’s LAN IP instead:

```txt
http://<YOUR-LAPTOP-LAN-IP>:8000
```

Example:

```txt
http://192.168.1.10:8000
```

---

## 3. Required Flutter screens

### 3.1 Request Screen

Purpose: User enters a natural-language service request.

Examples:

```txt
AC bilkul kaam nahi kar raha, kal subah G-13 mein technician chahiye
Plumber chahiye DHA phase 2 mein pani leak ho raha hai
Naai chahiye F-7 main jaldi, event pr jana hai sham ko
```

UI fields:

```txt
- Text input for service request
- Submit button
- Optional debug toggles:
  - simulate_maps_failure
  - simulate_no_providers
  - simulate_booking_failure
  - simulate_payment_failure
  - simulate_provider_cancellation
```

Submit to:

```txt
POST /api/orchestrate
```

---

### 3.2 Results / Booking Screen

Purpose: Show the orchestration result.

Sections:

```txt
- Request understanding card
- Selected provider card
- Top matches list
- Pricing card
- Booking/scheduling card
- Notifications card
- Lifecycle timeline
- Agent trace timeline
```

---

### 3.3 Pending Reschedule Screen

Show this when:

```json
"status": "pending_reschedule"
```

UI should display:

```txt
- Original assigned slot
- Conflict detected message
- Alternate slots
- Button for each alternate slot
```

When user selects a slot:

```txt
POST /api/booking/{booking_id}/select-slot
```

---

### 3.4 Feedback / Dispute Screen

Purpose: Submit post-service feedback.

Fields:

```txt
- Rating 1-5
- Feedback text
```

Submit to:

```txt
POST /api/feedback
```

Show response:

```txt
- Sentiment
- Complaint type
- Escalation required or not
- Compensation recommendation
- Reputation impact
- Future matching impact
```

---

### 3.5 Agent Trace / Replay Screen

Purpose: Show Antigravity-style workflow visibility.

Show each trace step as an expandable card:

```txt
Intent reasoning
Discovery/tool execution
Matching decision
Pricing calculation
Booking execution
Scheduling decision
Lifecycle follow-up
Fallback recovery
Feedback/dispute
Reputation memory update
```

Fields to show:

```txt
- step
- trace_type
- tool_called
- duration_ms
- summary
- input/output expandable JSON
```

---

## 4. API routes

## 4.1 Health check

### Request

```txt
GET /api/health
```

### Response

```json
{
  "status": "ok"
}
```

Use this to confirm backend connection.

---

## 4.2 Main orchestration route

### Request

```txt
POST /api/orchestrate
```

### Body

```json
{
  "message": "AC repair chahiye kal subah G-13 mein",
  "user_id": "user_001",
  "simulate_maps_failure": false,
  "simulate_no_providers": false,
  "simulate_booking_failure": false,
  "simulate_payment_failure": false,
  "simulate_provider_cancellation": false
}
```

Only `message` is required. Other flags are for demos/testing.

### Important statuses

```txt
lifecycle_completed
confirmed
pending_reschedule
no_providers
booking_pending_local_fallback
payment_confirmation_failed
replacement_provider_selected
clarification_needed
```

### Main response shape

```json
{
  "status": "lifecycle_completed",
  "fallback_response": null,
  "completion_evidence": {},
  "cancellation_fallback": null,
  "payment_fallback": null,
  "request_understanding": {},
  "selected_provider": {},
  "top_matches": [],
  "matching_reason": "...",
  "pricing": {},
  "booking": {},
  "lifecycle": {},
  "agent_trace": []
}
```

---

## 5. Rendering `/api/orchestrate` response

### 5.1 Request understanding card

Use:

```json
"request_understanding": {
  "service_type": "AC repair",
  "issue_description": "AC repair chahiye",
  "location": "G-13",
  "datetime_preference": "kal subah",
  "urgency": "unknown",
  "language_detected": "roman_urdu",
  "confidence": 0.95,
  "missing_fields": [],
  "clarification_question": null
}
```

Render:

```txt
Service: AC repair
Location: G-13
Time: kal subah
Language: roman_urdu
Confidence: 95%
```

If `clarification_question` is not null, show it and do not proceed to booking UI.

---

### 5.2 Selected provider card

Use:

```json
"selected_provider": {
  "name": "Ali AC Services",
  "address": "G-13 Markaz, Islamabad",
  "rating": 4.8,
  "distance_km": 2.1,
  "matching_score": 0.86,
  "source": "google_maps"
}
```

Render:

```txt
Provider name
Rating
Distance
Matching score
Source
```

---

### 5.3 Top matches list

Use:

```json
"top_matches": [
  {
    "name": "Ali AC Services",
    "rating": 4.8,
    "distance_km": 2.1,
    "matching_score": 0.86,
    "address": "...",
    "matching_scores": {
      "distance_score": 0.9,
      "rating_score": 0.8,
      "review_score": 0.7,
      "review_recency_score": 0.8,
      "on_time_score": 0.9,
      "cancellation_score": 0.95,
      "budget_score": 1,
      "complexity_score": 1,
      "reputation_score": 0.75,
      "future_matching_impact": 0
    }
  }
]
```

Render each provider with expandable “Why this match?” section.

Important fields to show in demo:

```txt
- distance_score
- on_time_score
- cancellation_score
- reputation_score
- future_matching_impact
```

This proves explainable matching and reputation memory.

---

### 5.4 Pricing card

Use:

```json
"pricing": {
  "price": 750,
  "currency": "PKR",
  "range": {
    "min": 675,
    "max": 862,
    "currency": "PKR"
  },
  "summary": "Estimated price is Rs 750...",
  "breakdown": {
    "base_rate": 500,
    "distance_km": 2.1,
    "travel_fee": 63,
    "urgency_multiplier": 1.25,
    "complexity_multiplier": 1,
    "budget_discount": 0,
    "final_price": 750
  }
}
```

Render:

```txt
Estimated price
Min/max range
Base fee
Travel fee
Urgency multiplier
Complexity multiplier
Budget discount
```

---

### 5.5 Booking/scheduling card

Use:

```json
"booking": {
  "booking_id": "SRV-XXXX",
  "status": "confirmed",
  "eta_minutes": 45,
  "scheduling": {
    "assigned_slot": "2026-05-20T10:00:00",
    "travel_buffer_minutes": 15,
    "slot_conflict_check": {
      "has_conflict": false,
      "conflicting_bookings": []
    },
    "alternate_slots": [],
    "scheduling_status": "slot_assigned"
  },
  "calendar": {},
  "notifications": {},
  "provider_optimization": {},
  "payment": {},
  "summary": "Booking confirmed...",
  "database_inserted": true
}
```

Render:

```txt
Booking ID
Booking status
ETA
Assigned slot
Travel buffer
Scheduling status
Calendar simulated status
Payment simulated status
Provider optimization note
```

If:

```json
"scheduling_status": "conflict_detected"
```

show alternate slot selection UI.

---

## 6. Alternate slot selection

### Request

```txt
POST /api/booking/{booking_id}/select-slot
```

### Body

```json
{
  "selected_slot": "2026-05-20T11:00:00"
}
```

### Response

```json
{
  "status": "slot_confirmed",
  "booking_id": "SRV-XXXX",
  "selected_slot": "2026-05-20T11:00:00",
  "database_updated": true,
  "message": "Alternate slot selected and booking confirmed."
}
```

After this, call:

```txt
GET /api/booking-status/{booking_id}
```

---

## 7. Booking status route

### Request

```txt
GET /api/booking-status/{booking_id}
```

### Response

```json
{
  "booking": {},
  "events": []
}
```

Use this to refresh booking state and lifecycle events.

---

## 8. Notifications route

### Request

```txt
GET /api/notifications/{booking_id}
```

### Response

```json
{
  "booking_id": "SRV-XXXX",
  "notifications": [
    {
      "recipient_type": "user",
      "channel": "in_app",
      "title": "Booking confirmed",
      "message": "Your booking is confirmed.",
      "status": "simulated"
    },
    {
      "recipient_type": "provider",
      "channel": "whatsapp_simulated",
      "title": "New job assigned",
      "message": "New job assigned for booking SRV-XXXX.",
      "status": "simulated"
    }
  ]
}
```

Flutter should show these as notification cards.

These are not real push notifications. They are persisted simulated notifications and are realtime-ready through Supabase.

---

## 9. Feedback / dispute route

### Request

```txt
POST /api/feedback
```

### Body

```json
{
  "booking_id": "SRV-XXXX",
  "rating": 2,
  "feedback_text": "Technician late aya aur zyada paisay liye."
}
```

### Response

```json
{
  "status": "feedback_processed",
  "quality_feedback": {
    "booking_id": "SRV-XXXX",
    "provider_name": "Ali AC Services",
    "rating": 2,
    "feedback_text": "Technician late aya aur zyada paisay liye.",
    "sentiment": "negative",
    "complaint_type": "price_dispute",
    "dispute_severity": "high",
    "escalation_required": true,
    "compensation_amount": 500,
    "provider_reputation_delta": -0.3,
    "future_matching_impact": -0.2,
    "resolution_status": "human_escalation_required",
    "database_inserted": true
  },
  "reputation_update": {
    "status": "updated",
    "new_reputation_score": 0.45,
    "future_matching_impact": -0.2
  },
  "agent_trace": []
}
```

Render:

```txt
Feedback processed
Complaint type
Escalation required
Compensation recommendation
Reputation update
Future matching impact
```

---

## 10. Lifecycle timeline

Lifecycle events come from either:

```txt
response.lifecycle.events
```

or:

```txt
GET /api/booking-status/{booking_id}
```

Expected statuses:

```txt
technician_assigned
on_the_way
in_progress
completed
feedback_requested
```

UI timeline:

```txt
✓ Technician assigned
✓ On the way
✓ Service started
✓ Service completed
✓ Feedback requested
```

If booking status is `pending_reschedule`, lifecycle will be null. This is correct.

---

## 11. Completion evidence

Use:

```json
"completion_evidence": {
  "booking_id": "SRV-XXXX",
  "completion_checklist": {
    "provider_arrived": false,
    "service_completed": false,
    "customer_confirmed": false,
    "issue_resolved": false,
    "payment_confirmed": false
  },
  "photo_evidence_required": true,
  "photo_evidence_url": null,
  "video_evidence_url": null,
  "evidence_status": "pending_upload"
}
```

Render as a checklist placeholder. No real media upload is required for now.

---

## 12. Failure and demo scenarios

### 12.1 Maps failure

```json
{
  "message": "AC repair chahiye kal G-13 mein",
  "user_id": "demo_user",
  "simulate_maps_failure": true
}
```

Expected:

```txt
Google Maps fails
→ mock fallback providers used
→ workflow continues
```

---

### 12.2 No providers

```json
{
  "message": "violin repair chahiye kal raat G-13 mein",
  "user_id": "demo_user",
  "simulate_no_providers": true
}
```

Expected:

```txt
status = no_providers
fallback_response shown
```

---

### 12.3 Payment failure

```json
{
  "message": "AC repair chahiye kal subah G-13 mein",
  "user_id": "payment_test",
  "simulate_payment_failure": true
}
```

Expected:

```txt
status = payment_confirmation_failed
payment_fallback shown
booking not finalized
```

---

### 12.4 Provider cancellation recovery

```json
{
  "message": "AC repair chahiye kal subah Bahria phase 6 mein",
  "user_id": "cancel_recovery_test",
  "simulate_provider_cancellation": true
}
```

Expected:

```txt
selected provider cancels
replacement provider selected
waitlist/recovery record created
reassignment notification generated
trace shows recovery
```

---

### 12.5 Scheduling conflict

Run the same request twice for the same time/provider.

Expected:

```txt
status = pending_reschedule
alternate_slots shown
lifecycle = null
```

---

## 13. Supabase Realtime recommendations

Flutter should use Supabase Realtime for:

```txt
booking_events
notifications
```

Recommended subscriptions:

```txt
booking_events where booking_id == active booking_id
notifications where booking_id == active booking_id
```

Do not implement custom WebSockets unless necessary. Supabase Realtime is enough.

---

## 14. Suggested Flutter state model

Create models:

```txt
OrchestrationResponse
RequestUnderstanding
Provider
MatchingScores
Pricing
Booking
Scheduling
NotificationItem
LifecycleEvent
AgentTrace
FeedbackResponse
```

Minimum fields should mirror the JSON keys above.

---

## 15. UX priority for judging

Most important UI features:

```txt
1. User submits Roman Urdu request
2. Agent timeline lights up step-by-step
3. Provider card explains why selected
4. Pricing breakdown is visible
5. Booking/lifecycle timeline is visible
6. Scheduling conflict shows alternate slots
7. Cancellation recovery shows replacement provider
8. Feedback dispute shows escalation and reputation impact
```

The frontend should make the backend orchestration visible. That is the main judging value.

---

## 16. What not to build now

Do not spend time on:

```txt
real push notifications
real WhatsApp integration
real media upload
real payment gateway
full provider dashboard
```

The backend already simulates these in a traceable way. Focus on UI clarity and demo flow.


"""
Simulated booking tool for schedule management, collision detection, and progress journey tracking.
"""

import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple


def parse_appointment_hour(time_str: str) -> int:
    """
    Parse hour from appointment time string. Supports formats like:
      - YYYY-MM-DD HH:MM
      - HH:MM (fallback)
    Defaults to 9 AM if parsing fails.
    """
    if not time_str:
        return 9
        
    try:
        # Match time part (e.g. 14:30 or 09:15)
        match = re.search(r"(\d{1,2}):(\d{2})", time_str)
        if match:
            return int(match.group(1))
            
        # Try full datetime parse
        for fmt in ("%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M", "%H:%M"):
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.hour
            except ValueError:
                continue
    except Exception:
        pass
    return 9


def generate_alternative_slots(time_str: str, distance_km: float = 5.0) -> List[str]:
    """
    Generate alternative schedule suggestions using dynamic travel-time buffers based on distance.
    - If distance <= 5km: short travel buffer (+1.5h, +3h)
    - If distance <= 15km: medium travel buffer (+2h, +4h)
    - If distance > 15km: long travel buffer (+3h, +5h)
    If they cross 8 PM (20:00), shift to next morning.
    """
    base_format = "%Y-%m-%d %H:%M"
    try:
        dt = datetime.strptime(time_str, base_format)
    except Exception:
        # If input format is custom, try to use current date
        now = datetime.now()
        dt = datetime(now.year, now.month, now.day, 14, 0)

    if distance_km <= 5.0:
        shifts = (1.5, 3.0)
    elif distance_km <= 15.0:
        shifts = (2.0, 4.0)
    else:
        shifts = (3.0, 5.0)

    alternatives = []
    for shift_hours in shifts:
        candidate_dt = dt + timedelta(hours=shift_hours)
        if candidate_dt.hour > 20 or candidate_dt.hour < 8:
            # Shift to next day morning
            next_day = candidate_dt + timedelta(days=1)
            if shift_hours == shifts[0]:
                alternative_slot = datetime(next_day.year, next_day.month, next_day.day, 9, 0)
            else:
                alternative_slot = datetime(next_day.year, next_day.month, next_day.day, 11, 30)
        else:
            alternative_slot = candidate_dt
        alternatives.append(alternative_slot.strftime(base_format))
        
    return alternatives


def check_booking_collision(
    provider_name: str,
    appointment_time: str,
    alternative_providers_pool: List[str] = None,
    distance_km: float = 5.0
) -> Tuple[str, List[str], List[str]]:
    """
    Check for schedule collision.
    
    Rule:
      If requested hour is EVEN (e.g., 10 AM, 12 PM, 2 PM, 4 PM), we simulate a scheduling conflict.
      If requested hour is ODD (e.g., 9 AM, 11 AM, 1 PM, 3 PM), the slot is available.
      
    Returns:
      Tuple of (status, alternative_slots, alternative_providers)
      Status can be "confirmed" or "conflict".
    """
    hour = parse_appointment_hour(appointment_time)

    if hour % 2 == 0:
        # Collision detected!
        alt_slots = generate_alternative_slots(appointment_time, distance_km)
        
        # Build alternative providers list
        if alternative_providers_pool:
            alt_provs = [p for p in alternative_providers_pool if p != provider_name][:2]
        else:
            alt_provs = ["Rizwan Cooling Center", "Capital Electric Works"]
            
        return "conflict", alt_slots, alt_provs
        
    return "confirmed", [], []


def generate_booking_receipt(booking_id: str, provider_name: str, price: float) -> Tuple[List[str], List[str], Dict[str, bool]]:
    """
    Generate simulated notification logs, service lifecycle milestones, and completion checklist.
    """
    reminders = [
        f"SMS reminder scheduled for 24 hours prior to appointment [ID: {booking_id}].",
        f"WhatsApp confirmation sent to customer for provider {provider_name}.",
        f"In-App push notification sent: 'Aapka partner {provider_name} aane ke liye tayyar hai!'"
    ]
    
    progress = [
        "Milestone 0: Booking Confirmed (Service successfully scheduled in DB)",
        f"Milestone 1: Partner Dispatched ({provider_name} has departed for your location)",
        f"Milestone 2: Arrived at Location (Provider arrived at G-13 Gole Market, Islamabad)",
        "Milestone 3: Inspection Started (Diagnosing the issue with safety protocols)",
        f"Milestone 4: Completed (Work completed. Billing of PKR {price} collected)"
    ]

    default_checklist = {
        "pre_inspection_done": True,
        "parts_checked": True,
        "cleanup_completed": True,
        "customer_signoff": True
    }
    
    return reminders, progress, default_checklist

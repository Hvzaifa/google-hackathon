"""
Simulated payment processing tool for ServisAI.

Provides a deterministic payment gateway simulation with configurable failure scenarios.
Supports JazzCash, EasyPaisa, and Card payment methods common in Pakistan.
"""

from typing import Dict, Any, Tuple
import random
import time


# Simulated payment method configs
SUPPORTED_METHODS = ["jazzcash", "easypaisa", "card", "cod"]

# In-memory ledger for tracking payment attempts
_payment_ledger: list = []


def simulate_payment(
    booking_id: str,
    total_price: float,
    payment_method: str = "jazzcash",
    force_failure: bool = False
) -> Tuple[str, Dict[str, Any]]:
    """
    Simulate a payment transaction for a service booking.

    Deterministic failure rule:
      - If total_price ends in .99 (e.g. 1999.99) -> simulate payment failure (insufficient funds)
      - If force_failure is True -> always fail
      - Otherwise -> payment succeeds

    Returns:
      Tuple of (status, payment_details)
      Status can be: "payment_success", "payment_failed", "payment_pending"
    """
    method = payment_method.lower() if payment_method else "jazzcash"
    if method not in SUPPORTED_METHODS:
        method = "jazzcash"

    transaction_id = f"TXN-{random.randint(100000, 999999)}"
    timestamp = time.time()

    payment_details = {
        "transaction_id": transaction_id,
        "booking_id": booking_id,
        "amount": total_price,
        "currency": "PKR",
        "payment_method": method,
        "timestamp": timestamp
    }

    # Deterministic failure: price ending in .99 or forced
    price_str = f"{total_price:.2f}"
    should_fail = force_failure or price_str.endswith(".99")

    if should_fail:
        payment_details["status"] = "failed"
        payment_details["failure_reason"] = (
            "Insufficient funds" if price_str.endswith(".99")
            else "Payment gateway timeout"
        )
        payment_details["retry_allowed"] = True
        payment_details["fallback_method"] = "cod"  # Cash on delivery fallback

        _payment_ledger.append(payment_details)
        return "payment_failed", payment_details

    # Success path
    payment_details["status"] = "success"
    payment_details["failure_reason"] = None
    payment_details["retry_allowed"] = False
    payment_details["fallback_method"] = None

    _payment_ledger.append(payment_details)
    return "payment_success", payment_details


def retry_payment_with_cod(
    booking_id: str,
    total_price: float
) -> Tuple[str, Dict[str, Any]]:
    """
    Retry a failed payment using Cash on Delivery (COD) as the fallback method.
    COD always succeeds but adds a PKR 50 COD handling surcharge.
    """
    transaction_id = f"TXN-COD-{random.randint(100000, 999999)}"
    cod_surcharge = 50.0
    final_amount = total_price + cod_surcharge

    payment_details = {
        "transaction_id": transaction_id,
        "booking_id": booking_id,
        "amount": final_amount,
        "original_amount": total_price,
        "cod_surcharge": cod_surcharge,
        "currency": "PKR",
        "payment_method": "cod",
        "status": "success",
        "failure_reason": None,
        "retry_allowed": False,
        "fallback_method": None,
        "timestamp": time.time(),
        "note": "Automatic COD fallback after digital payment failure"
    }

    _payment_ledger.append(payment_details)
    return "payment_success", payment_details


def get_payment_ledger() -> list:
    """Returns the full in-memory payment ledger for audit/debugging."""
    return list(_payment_ledger)

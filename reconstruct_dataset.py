"""
ReconGuard Synthetic Financial Dataset Generator
Track 01: Money, Risk & Regulation | ExaThon 2026 | Team codeleon

Generates ultra-realistic Core Banking System (CBS) transactions and Payment Gateway
settlement records with deterministic matching, fee discrepancies, timing drifts,
and fuzzy unstructured breaks for testing Exasol and AI reconciliation capabilities.
"""

import random
import uuid
import datetime
from typing import Tuple, List, Dict, Any

CHANNELS = ["UPI", "NEFT", "RTGS", "POS_CARD", "ECOM_GATEWAY", "SWIFT"]
GATEWAYS = {
    "UPI": "NPCI_UPI",
    "POS_CARD": "VISA_DIRECT",
    "ECOM_GATEWAY": "RAZORPAY",
    "NEFT": "RBI_NEFT",
    "RTGS": "RBI_RTGS",
    "SWIFT": "SWIFT_GPI"
}

MERCHANTS = [
    ("FLIPKART_INDIA", "Flipkart Internet Pvt Ltd"),
    ("AMAZON_PAY", "Amazon Pay India"),
    ("SWIGGY_FOODS", "Bundl Technologies Swiggy"),
    ("ZOMATO_LIMITED", "Zomato Ltd"),
    ("RELIANCE_RETAIL", "Reliance Retail JioMart"),
    ("APOLLO_PHARMACY", "Apollo Hospitals Pharmacy"),
    ("INDIGO_AIRLINES", "InterGlobe Aviation IndiGo"),
    ("MAKEMYTRIP", "MakeMyTrip India Pvt Ltd"),
    ("TATA_POWER", "Tata Power Co Ltd"),
    ("HDFC_LIFE", "HDFC Life Insurance")
]

CUSTOMER_NAMES = [
    "Aarav Sharma", "Diya Patel", "Rohan Iyer", "Ananya Reddy",
    "Vikram Malhotra", "Pooja Verma", "Siddharth Nair", "Meera Joshi",
    "Kabir Sen", "Ishaan Gupta", "Sneha Mukherjee", "Aditya Kulkarni"
]

def generate_reference_id(channel: str, seq: int) -> str:
    timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 10))).strftime("%y%m%d")
    rand_suffix = f"{random.randint(100000, 999999)}"
    if channel == "UPI":
        return f"UPI{timestamp}{seq:04d}{rand_suffix}"
    elif channel == "SWIFT":
        return f"SWF{timestamp}{seq:04d}{rand_suffix}"
    else:
        return f"REF{timestamp}{seq:04d}{rand_suffix}"

def create_synthetic_financial_dataset(n_records: int = 5000, seed: int = 42) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates CBS records and corresponding Gateway Settlement records.
    Breakdown:
      - 80% Clean 1:1 matches
      - 8% Fee deductions (MDR 1.5% - 2%)
      - 5% Timing drift across day cutoff (1-2 days lag)
      - 4% Fuzzy/Truncated narratives (Agent resolution targets)
      - 3% Suspense breaks (Missing gateway settlement or duplicate CBS)
    """
    random.seed(seed)
    cbs_records = []
    settlement_records = []

    base_time = datetime.datetime(2026, 10, 20, 9, 0, 0)

    for i in range(1, n_records + 1):
        txn_id = f"CBS_TXN_{i:06d}"
        account_id = f"ACC_{random.randint(10000000, 99999999)}"
        channel = random.choice(CHANNELS)
        gateway = GATEWAYS[channel]
        merchant_code, merchant_name = random.choice(MERCHANTS)
        customer = random.choice(CUSTOMER_NAMES)
        
        # Amount distribution (90% retail 100 - 50,000, 10% wholesale 50,000 - 2,000,000)
        if random.random() < 0.90:
            amount = round(random.uniform(150.0, 48500.0), 2)
        else:
            amount = round(random.uniform(50000.0, 1500000.0), 2)

        booking_time = base_time + datetime.timedelta(
            minutes=random.randint(0, 10000),
            seconds=random.randint(0, 59)
        )
        ref_id = generate_reference_id(channel, i)

        cbs_record = {
            "txn_id": txn_id,
            "account_id": account_id,
            "customer_name": customer,
            "amount": amount,
            "currency": "INR",
            "txn_type": "DEBIT",
            "booking_time": booking_time.strftime("%Y-%m-%d %H:%M:%S"),
            "reference_id": ref_id,
            "channel": channel,
            "description": f"{channel} transfer to {merchant_name} REF:{ref_id}",
            "status": "PENDING"
        }
        cbs_records.append(cbs_record)

        # Decide reconciliation profile
        dice = random.random()
        settlement_id = f"GW_SETTLE_{i:06d}"
        batch_id = f"BATCH_{(i // 100) + 1:04d}"

        if dice < 0.80:
            # 80%: Clean 1:1 match
            settle_time = booking_time + datetime.timedelta(minutes=random.randint(1, 45))
            settlement_records.append({
                "settlement_id": settlement_id,
                "gateway_name": gateway,
                "batch_id": batch_id,
                "gross_amount": amount,
                "fee_deducted": 0.00,
                "net_amount": amount,
                "currency": "INR",
                "settlement_time": settle_time.strftime("%Y-%m-%d %H:%M:%S"),
                "external_ref": ref_id,
                "narrative": f"SETTLEMENT {merchant_code} {ref_id}"
            })
        elif dice < 0.88:
            # 8%: MDR Fee Deducted (e.g. 1.75% fee taken by gateway)
            fee = round(amount * random.uniform(0.012, 0.022), 2)
            net_amt = round(amount - fee, 2)
            settle_time = booking_time + datetime.timedelta(hours=random.randint(1, 6))
            settlement_records.append({
                "settlement_id": settlement_id,
                "gateway_name": gateway,
                "batch_id": batch_id,
                "gross_amount": net_amt, # Gateway reports net amount disbursed
                "fee_deducted": fee,
                "net_amount": net_amt,
                "currency": "INR",
                "settlement_time": settle_time.strftime("%Y-%m-%d %H:%M:%S"),
                "external_ref": ref_id,
                "narrative": f"MERCHANT PAYOUT NET OF MDR {fee} {merchant_code} {ref_id}"
            })
        elif dice < 0.93:
            # 5%: Timing drift across bank cut-off
            settle_time = booking_time + datetime.timedelta(days=random.randint(2, 4))
            settlement_records.append({
                "settlement_id": settlement_id,
                "gateway_name": gateway,
                "batch_id": batch_id,
                "gross_amount": amount,
                "fee_deducted": 0.00,
                "net_amount": amount,
                "currency": "INR",
                "settlement_time": settle_time.strftime("%Y-%m-%d %H:%M:%S"),
                "external_ref": ref_id,
                "narrative": f"POST-CUTOFF DELAYED CLEARING {ref_id}"
            })
        elif dice < 0.97:
            # 4%: Fuzzy break (Narrative mutated, prefix stripped, or suffix missing)
            # Perfect showcase for Gemini Flash Governed AI
            settle_time = booking_time + datetime.timedelta(hours=random.randint(2, 12))
            truncated_ref = ref_id[3:] if len(ref_id) > 6 else ref_id # strips channel prefix
            settlement_records.append({
                "settlement_id": settlement_id,
                "gateway_name": gateway,
                "batch_id": batch_id,
                "gross_amount": amount,
                "fee_deducted": 0.00,
                "net_amount": amount,
                "currency": "INR",
                "settlement_time": settle_time.strftime("%Y-%m-%d %H:%M:%S"),
                "external_ref": f"EXT-{truncated_ref}", # mutated external reference
                "narrative": f"MANUAL REMITTANCE PAYEE:{merchant_code} MATCH_TAG:{truncated_ref}"
            })
        else:
            # 3%: Suspense item (No settlement record created - True break in suspense)
            pass

    return cbs_records, settlement_records

if __name__ == "__main__":
    cbs, gw = create_synthetic_financial_dataset(n_records=100)
    print(f"Generated {len(cbs)} CBS transactions and {len(gw)} Gateway settlements.")
    print("Sample CBS Transaction:", cbs[0])
    print("Sample Settlement:", gw[0])

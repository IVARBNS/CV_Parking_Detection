from datetime import datetime, timedelta
from collections import defaultdict
import json, os
import numpy as np
from config import PricingConfig, PricingTier

BILLING_PATH = "/Data/billing_data/billing_report.json"


class RevenueManager:
    """Manages parking revenue tracking and billing"""

    def __init__(self, config=PricingConfig()):
        self.config = config
        self.sessions = []  # List of completed parking sessions
        self.active_sessions = {}  # spot_id -> session data
        self.revenue_by_spot = defaultdict(float)
        self.total_revenue = 0.0
        self.billing_records = []

    def start_session(self, spot_id, entry_time, pricing_tier=PricingTier.HOURLY):
        """Start a new parking session"""
        session = {
            "spot_id": spot_id,
            "entry_time": entry_time,
            "pricing_tier": pricing_tier,
            "exit_time": None,
            "duration": None,
            "fee": 0.0,
            "session_id": f"S{spot_id}-{entry_time.strftime('%Y%m%d%H%M%S')}",
        }
        self.active_sessions[spot_id] = session
        return session

    def end_session(self, spot_id, exit_time):
        """End a parking session and calculate fee"""
        if spot_id not in self.active_sessions:
            return None

        session = self.active_sessions[spot_id]
        session["exit_time"] = exit_time
        session["duration"] = exit_time - session["entry_time"]

        # Calculate fee based on pricing tier
        fee = self.calculate_fee(
            session["duration"], session["pricing_tier"], session["entry_time"]
        )
        session["fee"] = fee

        # Update revenue tracking
        self.total_revenue += fee
        self.revenue_by_spot[spot_id] += fee
        self.sessions.append(session)

        # Generate billing record
        self.generate_billing_record(session)

        # Remove from active sessions
        del self.active_sessions[spot_id]

        return session

    def calculate_fee(self, duration, pricing_tier, entry_time):
        """Calculate parking fee based on duration and pricing tier"""
        total_minutes = duration.total_seconds() / 60

        if pricing_tier == PricingTier.MONTHLY:
            return self.config.MONTHLY_RATE

        elif pricing_tier == PricingTier.DAILY:
            days = max(1, int(np.ceil(duration.total_seconds() / (24 * 3600))))
            return days * self.config.DAILY_RATE

        else:  # HOURLY
            # Apply grace period
            if total_minutes <= self.config.HOURLY_GRACE_PERIOD_MINUTES:
                return 0.0

            # Calculate billable minutes
            billable_minutes = total_minutes - self.config.HOURLY_GRACE_PERIOD_MINUTES
            hours = billable_minutes / 60

            # Check for peak hours
            fee = hours * self.config.HOURLY_RATE
            if self.is_peak_hour(entry_time):
                fee *= self.config.PEAK_MULTIPLIER

            return round(fee, 2)

    def is_peak_hour(self, dt):
        """Check if time falls within peak hours"""
        hour = dt.hour
        for start, end in self.config.PEAK_HOURS:
            if start <= hour < end:
                return True
        return False

    def get_current_fee(self, spot_id, current_time):
        """Get current estimated fee for an active session"""
        if spot_id not in self.active_sessions:
            return 0.0

        session = self.active_sessions[spot_id]
        duration = current_time - session["entry_time"]
        return self.calculate_fee(
            duration, session["pricing_tier"], session["entry_time"]
        )

    def generate_billing_record(self, session):
        """Generate a billing record for a completed session"""
        record = {
            "session_id": session["session_id"],
            "spot_id": session["spot_id"],
            "entry_time": session["entry_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "exit_time": session["exit_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "duration": str(session["duration"]),
            "pricing_tier": session["pricing_tier"].value,
            "fee": f"${session['fee']:.2f}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.billing_records.append(record)

    def export_billing_report(self, filename=BILLING_PATH):
        """Export billing records to JSON file"""
        report = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_sessions": len(self.sessions),
            "total_revenue": f"${self.total_revenue:.2f}",
            "revenue_by_spot": {
                k: f"${v:.2f}" for k, v in self.revenue_by_spot.items()
            },
            "billing_records": self.billing_records,
        }

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Billing report exported to {filename}")

    def get_revenue_summary(self):
        """Get comprehensive revenue summary"""
        if not self.sessions:
            return {
                "total_revenue": 0.0,
                "total_sessions": 0,
                "avg_fee": 0.0,
                "avg_duration": timedelta(0),
            }

        total_duration = sum((s["duration"] for s in self.sessions), timedelta(0))

        return {
            "total_revenue": self.total_revenue,
            "total_sessions": len(self.sessions),
            "avg_fee": self.total_revenue / len(self.sessions),
            "avg_duration": total_duration / len(self.sessions),
            "revenue_by_spot": dict(self.revenue_by_spot),
            "active_sessions": len(self.active_sessions),
        }

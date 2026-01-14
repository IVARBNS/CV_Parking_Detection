from datetime import datetime, timedelta
from config import PricingTier

class ParkingSpotTracker:
    """Tracks individual parking spot status and revenue"""
    
    def __init__(self, spot_id, position, revenue_manager):
        self.spot_id = spot_id
        self.position = position  # (x1, y1, w, h)
        self.is_occupied = False
        self.occupation_start_time = None
        self.occupation_duration = timedelta(0)
        self.total_occupation_time = timedelta(0)
        self.occupation_count = 0
        self.last_status_change = None
        self.revenue_manager = revenue_manager
        self.pricing_tier = PricingTier.HOURLY  # Default pricing
        
    def update_status(self, is_occupied, current_time):
        """Update occupation status and duration tracking"""
        if is_occupied and not self.is_occupied:
            # Car just arrived
            self.is_occupied = True
            self.occupation_start_time = current_time
            self.last_status_change = current_time
            self.occupation_count += 1
            
            # Start revenue session
            self.revenue_manager.start_session(
                self.spot_id, 
                current_time, 
                self.pricing_tier
            )
            
        elif not is_occupied and self.is_occupied:
            # Car just left
            if self.occupation_start_time:
                duration = current_time - self.occupation_start_time
                self.occupation_duration = duration
                self.total_occupation_time += duration
                
                # End revenue session
                self.revenue_manager.end_session(self.spot_id, current_time)
                
            self.is_occupied = False
            self.occupation_start_time = None
            self.last_status_change = current_time
            
        elif is_occupied and self.is_occupied:
            # Car still present - update current duration
            if self.occupation_start_time:
                self.occupation_duration = current_time - self.occupation_start_time
    
    def get_current_duration(self, current_time):
        """Get current parking duration"""
        if self.is_occupied and self.occupation_start_time:
            return current_time - self.occupation_start_time
        return timedelta(0)
    
    def get_current_fee(self, current_time):
        """Get current estimated fee"""
        return self.revenue_manager.get_current_fee(self.spot_id, current_time)
    
    def is_overstaying(self, current_time, threshold_minutes):
        """Check if vehicle is overstaying"""
        if self.is_occupied:
            duration = self.get_current_duration(current_time)
            return duration.total_seconds() / 60 > threshold_minutes
        return False
    
    def set_pricing_tier(self, tier):
        """Set pricing tier for this spot"""
        self.pricing_tier = tier
    
    def get_stats(self):
        """Get parking spot statistics"""
        return {
            'spot_id': self.spot_id,
            'is_occupied': self.is_occupied,
            'current_duration': self.occupation_duration,
            'total_time': self.total_occupation_time,
            'occupation_count': self.occupation_count,
            'pricing_tier': self.pricing_tier.value
        }
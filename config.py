from enum import Enum

class PricingTier(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"

class PricingConfig:
    """Parking pricing configuration"""
    # Hourly rates (per hour)
    HOURLY_RATE = 5.0
    HOURLY_GRACE_PERIOD_MINUTES = 15  # First 15 minutes free
    
    # Daily pass
    DAILY_RATE = 30.0
    DAILY_MAX_HOURS = 24
    
    # Monthly pass
    MONTHLY_RATE = 400.0
    
    # Peak hour multiplier (optional)
    PEAK_HOURS = [(7, 9), (17, 19)]  # 7-9 AM, 5-7 PM
    PEAK_MULTIPLIER = 1.5

class SystemConfig:
    """System configuration"""
    # Video and mask paths
    MASK_PATH = 'mask_1920_1080.png'
    VIDEO_PATH = r'C:\Users\Admin\Desktop\FILES\CV\Data\data\parking_1920_1080_loop.mp4'
    
    # Processing settings
    FRAME_STEP = 30  # Process every Nth frame
    OVERSTAY_THRESHOLD_MINUTES = 120  # 2 hours
    
    # Statistics settings
    STATS_PRINT_INTERVAL = 30  # Print stats every N seconds
    
    # Premium spots (using daily rate)
    PREMIUM_SPOT_COUNT = 5  # First N spots are premium
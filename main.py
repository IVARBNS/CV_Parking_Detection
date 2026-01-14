import cv2
import numpy as np
from datetime import datetime
import time

from utils import get_parking_spots_bboxes, empty_or_not, calc_diff
from config import SystemConfig, PricingConfig, PricingTier
from revenue_manager import RevenueManager
from parking_tracker import ParkingSpotTracker
from visualization import draw_enhanced_overlay, print_statistics

BILLING_PATH_final = f"Data/billing_data/final_billing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"
BILLING_PATH_r = (
    f"Data/billing_data/billing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"
)


def main():
    """Main application entry point"""

    # Load configuration
    config = SystemConfig()

    # Load mask and video
    mask = cv2.imread(config.MASK_PATH, 0)
    cap = cv2.VideoCapture(config.VIDEO_PATH)

    # Get bounding boxes
    bboxs = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    spots = get_parking_spots_bboxes(bboxs)

    # Initialize revenue manager
    revenue_manager = RevenueManager()

    # Initialize trackers for each parking spot
    trackers = [
        ParkingSpotTracker(spot_id=i, position=spot, revenue_manager=revenue_manager)
        for i, spot in enumerate(spots)
    ]

    # Set different pricing tiers for premium spots
    for i in range(min(config.PREMIUM_SPOT_COUNT, len(trackers))):
        trackers[i].set_pricing_tier(PricingTier.DAILY)

    # Processing variables
    previous_frame = None
    spots_status = [None for _ in spots]
    diffs = [None for _ in spots]
    frame_number = 0
    ret = True

    # For statistics printing
    last_stats_print = time.time()

    # Print startup information
    print("=" * 70)
    print("PARKING LOT REVENUE MANAGEMENT SYSTEM")
    print("=" * 70)
    print(f"\nPricing Configuration:")
    print(f"  Hourly Rate: ${PricingConfig.HOURLY_RATE}/hour")
    print(f"  Daily Pass: ${PricingConfig.DAILY_RATE}/day")
    print(f"  Monthly Pass: ${PricingConfig.MONTHLY_RATE}/month")
    print(f"  Grace Period: {PricingConfig.HOURLY_GRACE_PERIOD_MINUTES} minutes")
    print(f"  Peak Hour Multiplier: {PricingConfig.PEAK_MULTIPLIER}x")
    print("\nPress 'q' to quit, 'r' to generate revenue report")
    print("=" * 70)

    while ret:
        ret, frame = cap.read()

        if not ret:
            break

        current_time = datetime.now()

        # Calculate differences for motion detection
        if frame_number % config.FRAME_STEP == 0 and previous_frame is not None:
            for spot_index, spot in enumerate(spots):
                x1, y1, w, h = spot
                spot_crop = frame[y1 : y1 + h, x1 : x1 + w, :]
                diffs[spot_index] = calc_diff(
                    spot_crop, previous_frame[y1 : y1 + h, x1 : x1 + w, :]
                )

        # Update spot status
        if frame_number % config.FRAME_STEP == 0:
            if previous_frame is None:
                arr_ = range(len(spots))
            else:
                arr_ = [
                    j
                    for j in np.argsort(diffs)
                    if diffs[j] and (diffs[j] / np.amax(diffs)) > 0.4
                ]

            for spot_index in arr_:
                spot = spots[spot_index]
                x1, y1, w, h = spot
                spot_crop = frame[y1 : y1 + h, x1 : x1 + w, :]
                spot_status = empty_or_not(spot_crop)
                spots_status[spot_index] = spot_status

                # Update tracker
                trackers[spot_index].update_status(not spot_status, current_time)

        if frame_number % config.FRAME_STEP == 0:
            previous_frame = frame.copy()

        # Draw enhanced overlay with revenue
        draw_enhanced_overlay(
            frame, trackers, spots, revenue_manager, config.OVERSTAY_THRESHOLD_MINUTES
        )

        # Print statistics periodically
        if time.time() - last_stats_print > config.STATS_PRINT_INTERVAL:
            print_statistics(trackers, revenue_manager)
            last_stats_print = time.time()

        # Display frame
        cv2.namedWindow("Parking Revenue Management", cv2.WINDOW_NORMAL)
        cv2.imshow("Parking Revenue Management", frame)

        key = cv2.waitKey(25) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r"):
            # Generate revenue report on demand
            revenue_manager.export_billing_report(BILLING_PATH_r)

        frame_number += 1

    # Final statistics and export
    print("\n" + "=" * 70)
    print("FINAL STATISTICS & REVENUE REPORT")
    print_statistics(trackers, revenue_manager)

    # Export final billing report
    revenue_manager.export_billing_report(BILLING_PATH_final)

    cap.release()
    cv2.destroyAllWindows()

    print("\n✓ System shutdown complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

import cv2
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
import time

from util import get_parking_spots_bboxes, empty_or_not, calc_diff

# Configuration
mask = "mask_1920_1080.png"
video_path = r"C:\Users\Admin\Desktop\FILES\CV\Data\data\parking_1920_1080_loop.mp4"
OVERSTAY_THRESHOLD_MINUTES = 120  # 2 hours for parking violation


# Simple tracking class to replace SORT/DeepSORT
class ParkingSpotTracker:
    def __init__(self, spot_id, position):
        self.spot_id = spot_id
        self.position = position  # (x1, y1, w, h)
        self.is_occupied = False
        self.occupation_start_time = None
        self.occupation_duration = timedelta(0)
        self.total_occupation_time = timedelta(0)
        self.occupation_count = 0
        self.last_status_change = None

    def update_status(self, is_occupied, current_time):
        """Update occupation status and duration tracking"""
        if is_occupied and not self.is_occupied:
            # Car just arrived
            self.is_occupied = True
            self.occupation_start_time = current_time
            self.last_status_change = current_time
            self.occupation_count += 1

        elif not is_occupied and self.is_occupied:
            # Car just left
            if self.occupation_start_time:
                duration = current_time - self.occupation_start_time
                self.occupation_duration = duration
                self.total_occupation_time += duration
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

    def is_overstaying(self, current_time, threshold_minutes):
        """Check if vehicle is overstaying"""
        if self.is_occupied:
            duration = self.get_current_duration(current_time)
            return duration.total_seconds() / 60 > threshold_minutes
        return False

    def get_stats(self):
        """Get parking spot statistics"""
        return {
            "spot_id": self.spot_id,
            "is_occupied": self.is_occupied,
            "current_duration": self.occupation_duration,
            "total_time": self.total_occupation_time,
            "occupation_count": self.occupation_count,
        }


def format_duration(duration):
    """Format timedelta to readable string"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def draw_enhanced_overlay(frame, trackers, spots):
    """Draw comprehensive parking information overlay"""
    # Count statistics
    total_spots = len(trackers)
    occupied = sum(1 for t in trackers if t.is_occupied)
    available = total_spots - occupied
    overstaying = sum(
        1
        for t in trackers
        if t.is_overstaying(datetime.now(), OVERSTAY_THRESHOLD_MINUTES)
    )

    # Draw main info panel
    panel_height = 130
    cv2.rectangle(frame, (20, 20), (350, panel_height), (0, 0, 0), -1)
    cv2.rectangle(frame, (20, 20), (350, panel_height), (255, 255, 255), 2)

    y_offset = 50
    cv2.putText(
        frame,
        f"Available: {available} / {total_spots}",
        (40, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
    )

    y_offset += 35
    cv2.putText(
        frame,
        f"Occupied: {occupied}",
        (40, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    y_offset += 35
    color = (0, 0, 255) if overstaying > 0 else (255, 255, 255)
    cv2.putText(
        frame,
        f"Violations: {overstaying}",
        (40, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
    )

    # Draw individual spot information
    current_time = datetime.now()
    for tracker in trackers:
        x1, y1, w, h = tracker.position

        if tracker.is_occupied:
            duration = tracker.get_current_duration(current_time)
            is_violation = tracker.is_overstaying(
                current_time, OVERSTAY_THRESHOLD_MINUTES
            )

            # Color coding: Red for violations, Yellow for occupied
            color = (0, 0, 255) if is_violation else (0, 165, 255)
            cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 3)

            # Draw duration label
            duration_text = format_duration(duration)
            label_bg_color = (0, 0, 200) if is_violation else (0, 100, 200)

            # Calculate text size for background
            (text_width, text_height), _ = cv2.getTextSize(
                duration_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            # Draw background for text
            # cv2.rectangle(
            #     frame, (x1, y1 - 25), (x1 + text_width + 10, y1 - 5), label_bg_color, -1
            # )
            cv2.putText(
                frame,
                duration_text,
                (x1 + 5, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                label_bg_color,
                2,
            )

            # Add violation warning
            if is_violation:
                cv2.putText(
                    frame,
                    "VIOLATION",
                    (x1 + 5, y1 + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
        else:
            # Available spot - green rectangle
            cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)

            # Show spot number
            cv2.putText(
                frame,
                f"#{tracker.spot_id}",
                (x1 + 5, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )


def print_statistics(trackers):
    """Print detailed parking statistics"""
    print("\n" + "=" * 60)
    print("PARKING LOT STATISTICS")
    print("=" * 60)

    for tracker in trackers:
        stats = tracker.get_stats()
        status = "OCCUPIED" if stats["is_occupied"] else "AVAILABLE"
        print(f"\nSpot #{stats['spot_id']}: {status}")

        if stats["is_occupied"]:
            print(f"  Current Duration: {format_duration(stats['current_duration'])}")

        print(f"  Total Occupations: {stats['occupation_count']}")
        print(f"  Total Time Occupied: {format_duration(stats['total_time'])}")

    # Overall statistics
    total_spots = len(trackers)
    occupied = sum(1 for t in trackers if t.is_occupied)
    total_time = sum((t.total_occupation_time.total_seconds() for t in trackers), 0)

    print("\n" + "-" * 60)
    print(
        f"Overall Occupancy Rate: {occupied}/{total_spots} ({100*occupied/total_spots:.1f}%)"
    )
    print(f"Total Parking Time: {format_duration(timedelta(seconds=total_time))}")
    print("=" * 60 + "\n")


# Main execution
mask = cv2.imread(mask, 0)
cap = cv2.VideoCapture(video_path)

# Get bounding boxes
bboxs = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
spots = get_parking_spots_bboxes(bboxs)

# Initialize trackers for each parking spot
trackers = [
    ParkingSpotTracker(spot_id=i, position=spot) for i, spot in enumerate(spots)
]

# Processing variables
previous_frame = None
spots_status = [None for _ in spots]
diffs = [None for _ in spots]
frame_number = 0
ret = True
step = 30
start_time = datetime.now()

# For statistics printing
last_stats_print = time.time()
stats_interval = 30  # Print stats every 30 seconds

while ret:
    ret, frame = cap.read()

    if not ret:
        break

    current_time = datetime.now()

    # Calculate differences for motion detection
    if frame_number % step == 0 and previous_frame is not None:
        for spot_index, spot in enumerate(spots):
            x1, y1, w, h = spot
            spot_crop = frame[y1 : y1 + h, x1 : x1 + w, :]
            diffs[spot_index] = calc_diff(
                spot_crop, previous_frame[y1 : y1 + h, x1 : x1 + w, :]
            )

    # Update spot status
    if frame_number % step == 0:
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

    if frame_number % step == 0:
        previous_frame = frame.copy()

    # Draw enhanced overlay
    draw_enhanced_overlay(frame, trackers, spots)

    # Print statistics periodically
    if time.time() - last_stats_print > stats_interval:
        print_statistics(trackers)
        last_stats_print = time.time()

    # Display frame
    cv2.namedWindow("Parking Lot Monitor", cv2.WINDOW_NORMAL)
    cv2.imshow("Parking Lot Monitor", frame)

    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

    frame_number += 1

# Final statistics
print("\n" + "=" * 60)
print("FINAL STATISTICS")
print_statistics(trackers)

cap.release()
cv2.destroyAllWindows()

import cv2
from datetime import datetime
from utils import format_duration


def draw_enhanced_overlay(frame, trackers, spots, revenue_manager, overstay_threshold):
    """Draw comprehensive parking information overlay with revenue"""
    current_time = datetime.now()

    # Count statistics
    total_spots = len(trackers)
    occupied = sum(1 for t in trackers if t.is_occupied)
    available = total_spots - occupied
    overstaying = sum(
        1 for t in trackers if t.is_overstaying(current_time, overstay_threshold)
    )

    # Revenue statistics
    revenue_summary = revenue_manager.get_revenue_summary()

    # Draw main info panel
    panel_height = 220
    cv2.rectangle(frame, (20, 20), (650, panel_height), (0, 0, 0), -1)
    cv2.rectangle(frame, (20, 20), (650, panel_height), (255, 255, 255), 2)

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

    # Revenue information
    y_offset += 40
    cv2.line(frame, (40, y_offset - 15), (630, y_offset - 15), (255, 255, 255), 1)

    cv2.putText(
        frame,
        f'Total Revenue: ${revenue_summary["total_revenue"]:.2f}',
        (40, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
    )

    y_offset += 35
    cv2.putText(
        frame,
        f'Total Sessions: {revenue_summary["total_sessions"]}',
        (40, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        1,
    )

    y_offset += 30
    if revenue_summary["total_sessions"] > 0:
        cv2.putText(
            frame,
            f'Avg Fee: ${revenue_summary["avg_fee"]:.2f}',
            (40, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            1,
        )

    # Draw individual spot information
    for tracker in trackers:
        x1, y1, w, h = tracker.position

        if tracker.is_occupied:
            duration = tracker.get_current_duration(current_time)
            current_fee = tracker.get_current_fee(current_time)
            is_violation = tracker.is_overstaying(current_time, overstay_threshold)

            # Color coding: Red for violations, Yellow for occupied
            color = (0, 0, 255) if is_violation else (0, 165, 255)
            cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 3)

            # Draw duration and fee labels
            duration_text = format_duration(duration)
            fee_text = f"${current_fee:.2f}"

            # Duration label
            label_bg_color = (0, 0, 200) if is_violation else (0, 100, 200)
            (text_width, text_height), _ = cv2.getTextSize(
                duration_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            cv2.rectangle(
                frame, (x1, y1 - 25), (x1 + text_width + 10, y1 - 5), label_bg_color, -1
            )
            cv2.putText(
                frame,
                duration_text,
                (x1 + 5, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            # Fee label
            (fee_width, fee_height), _ = cv2.getTextSize(
                fee_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                frame,
                (x1, y1 + h + 5),
                (x1 + fee_width + 10, y1 + h + 25),
                (0, 200, 0),
                -1,
            )
            cv2.putText(
                frame,
                fee_text,
                (x1 + 5, y1 + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            # Add violation warning
            if is_violation:
                cv2.putText(
                    frame,
                    "VIOLATION",
                    (x1 + 5, y1 + h + 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
        else:
            # Available spot - green rectangle
            cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)

            # Show spot number
            spot_info = f"#{tracker.spot_id}"
            cv2.putText(
                frame,
                spot_info,
                (x1 + 5, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )


def print_statistics(trackers, revenue_manager):
    """Print detailed parking and revenue statistics"""
    print("\n" + "=" * 70)
    print("PARKING LOT STATISTICS & REVENUE REPORT")
    print("=" * 70)

    # Revenue summary
    revenue_summary = revenue_manager.get_revenue_summary()
    print("\n--- REVENUE SUMMARY ---")
    print(f"Total Revenue: ${revenue_summary['total_revenue']:.2f}")
    print(f"Total Sessions: {revenue_summary['total_sessions']}")
    print(f"Active Sessions: {revenue_summary['active_sessions']}")

    if revenue_summary["total_sessions"] > 0:
        print(f"Average Fee per Session: ${revenue_summary['avg_fee']:.2f}")
        print(f"Average Duration: {format_duration(revenue_summary['avg_duration'])}")

    # Revenue by spot
    if revenue_summary["revenue_by_spot"]:
        print("\n--- REVENUE BY SPOT ---")
        sorted_spots = sorted(
            revenue_summary["revenue_by_spot"].items(), key=lambda x: x[1], reverse=True
        )
        for spot_id, revenue in sorted_spots[:10]:  # Top 10 revenue spots
            print(f"  Spot #{spot_id}: ${revenue:.2f}")

    # Parking spot details
    print("\n--- SPOT DETAILS ---")
    for tracker in trackers:
        stats = tracker.get_stats()
        status = "OCCUPIED" if stats["is_occupied"] else "AVAILABLE"
        print(f"\nSpot #{stats['spot_id']}: {status} ({stats['pricing_tier']})")

        if stats["is_occupied"]:
            current_fee = tracker.get_current_fee(datetime.now())
            print(f"  Current Duration: {format_duration(stats['current_duration'])}")
            print(f"  Current Fee: ${current_fee:.2f}")

        print(f"  Total Occupations: {stats['occupation_count']}")
        print(f"  Total Time Occupied: {format_duration(stats['total_time'])}")

    # Overall statistics
    total_spots = len(trackers)
    occupied = sum(1 for t in trackers if t.is_occupied)

    print("\n" + "-" * 70)
    print(
        f"Overall Occupancy Rate: {occupied}/{total_spots} ({100*occupied/total_spots:.1f}%)"
    )
    print("=" * 70 + "\n")

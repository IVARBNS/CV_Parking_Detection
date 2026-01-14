````markdown
# Parking Revenue Management System

A comprehensive parking lot monitoring system with revenue tracking, billing, and violation detection.

## Features

- **Real-time parking spot detection**
- **Multiple pricing tiers** (Hourly, Daily, Monthly)
- **Revenue tracking** per spot and overall
- **Automated billing** with JSON export
- **Violation detection** for overstaying vehicles
- **Peak hour pricing**
- **Grace period support**

## Installation

```bash
pip install -r requirements.txt
```
````

## Usage

```bash
python main.py
```

### Keyboard Controls

- `q` - Quit application
- `r` - Generate revenue report

## Configuration

Edit `config.py` to customize:

- Pricing rates
- Video/mask paths
- Processing parameters
- Premium spot count

## File Structure

- `main.py` - Application entry point
- `config.py` - Configuration settings
- `revenue_manager.py` - Revenue and billing logic
- `parking_tracker.py` - Spot tracking
- `visualization.py` - UI rendering
- `utils.py` - Utility functions

## Output

- Real-time video display with revenue overlay
- Console statistics every 30 seconds
- JSON billing reports on demand
- Final billing report on exit

````

---

## Implementation Instructions

1. **Create the directory structure**:
```bash
mkdir parking_system
cd parking_system
````

2. **Create each file** with the content above

3. **Run the system**:

```bash
python main.py
```

## Data

Download the data and model used in this project [here](https://drive.google.com/file/d/1Vb9xRe9dzSo0RQOMLuLJXkvNKfRGxnNt/view?usp=sharing)

```

```

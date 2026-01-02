# Rubik's Cube Solver (Webcam)

This tool uses your laptop's webcam to scan a Rubik's Cube and generates a step-by-step solution.

## Prerequisites

- Python 3.6+
- A webcam
- Good lighting (Daylight is best to distinguish Red vs Orange and White vs Yellow)

## Installation

1.  Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script:

```bash
python main.py
```

## How to Scan

The script will ask you to show each face of the cube in a specific order based on the **center sticker**.

1.  **UP** (White Center)
2.  **RIGHT** (Red Center)
3.  **FRONT** (Green Center)
4.  **DOWN** (Yellow Center)
5.  **LEFT** (Orange Center)
6.  **BACK** (Blue Center)

Align the cube with the 3x3 grid on screen. Ensure the small colored dots in the center of each grid cell match the sticker color.
Press **SPACE** to capture.
Press **Q** to quit.

## Troubleshooting

-   **Wrong Colors?** Adjust your lighting. Glare on the cube can make colors look white. Shadows can make them look black/blue.
-   **"Error: Could not find solution"**: This means one or more stickers were misidentified, making the cube state impossible. Try again.

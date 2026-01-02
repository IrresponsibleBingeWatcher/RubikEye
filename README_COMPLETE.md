# Rubik's Cube Solver - Complete Guide

Webcam-based Rubik's Cube solver that scans your cube and provides step-by-step solving instructions with physical orientation guidance.

## Quick Start

```bash
# Run the recommended version
python main_v5.py
```

## Version Guide

### ⭐ main_v5.py (RECOMMENDED)
**Best for beginners!** Includes physical cube holding instructions.

Features:
- ✅ Mirror flip correction
- ✅ Step-by-step scanning guidance
- ✅ HSV-based color detection
- ✅ **Physical orientation instructions** (NEW!)
- ✅ Tells you how to hold the cube for each move

Example output:
```
Step 1:
  Hold: Green facing you, White on top
  Turn FRONT (facing you) (Green) Clockwise (right)
  [F]
```

**Use this if**: You want the easiest-to-follow solution instructions.

---

### main_v4.py
Reliable version without Lab re-classification issues.

Features:
- ✅ Mirror flip correction
- ✅ Step-by-step scanning guidance
- ✅ HSV-based color detection
- ✅ Color distribution validation
- ❌ No physical orientation instructions

**Use this if**: You're comfortable with standard cube notation and just need the moves.

---

### main_v3.py (Has Issues)
⚠️ **Not recommended** - Lab color re-classification causes problems

---

### main_v2.py (Basic Fix)
Basic mirror flip fix only. No scanning guidance.

---

### main.py (Original)
⚠️ **Has mirror flip bug** - Use v2 or later instead

---

## Features Comparison

| Feature | v1 | v2 | v3 | v4 | v5 |
|---------|----|----|----|----|-----|
| Mirror flip fix | ❌ | ✅ | ✅ | ✅ | ✅ |
| Scanning guidance | ❌ | ❌ | ✅ | ✅ | ✅ |
| Face validation | ❌ | ❌ | ✅ | ✅ | ✅ |
| Lab re-classification | ❌ | ❌ | ⚠️ | ❌ | ❌ |
| Color distribution check | ❌ | ❌ | ❌ | ✅ | ✅ |
| Physical orientation | ❌ | ❌ | ❌ | ❌ | ⭐ |

## Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.6+
- Webcam
- Good lighting (natural daylight recommended)

Dependencies (installed via requirements.txt):
- opencv-python
- numpy
- kociemba

## Usage

### Step 1: Scan the Cube

```bash
python main_v5.py
```

Follow the on-screen instructions to scan all 6 faces:

1. **UP (White)** - Green edge at BOTTOM of camera view
2. **RIGHT (Red)** - Rotate right, White edge at TOP
3. **FRONT (Green)** - Rotate right, White edge at TOP
4. **DOWN (Yellow)** - Rotate right, flip cube, Green edge at TOP
5. **LEFT (Orange)** - Rotate right, White edge at TOP
6. **BACK (Blue)** - Rotate right, White edge at TOP

Hold each face steady for 3 seconds until captured.

Controls:
- **Hold steady** - Auto-captures after 3 seconds
- **R** - Restart scanning
- **Q** - Quit

### Step 2: Follow the Solution

The program will output step-by-step instructions like:

```
Step 1:
  Hold: Green facing you, White on top
  Turn FRONT (facing you) (Green) Clockwise (right)
  [F]

Step 2:
  Hold: Green facing you, White on top
  Turn RIGHT (Red) Clockwise (right)
  [R]
```

Simply follow each step in order!

## Troubleshooting

### "Invalid cube state" Error

**Cause**: Color detection issues

**Solutions**:
1. **Improve lighting** (most common fix)
   - Use natural daylight
   - Avoid glare on stickers
   - Avoid shadows
   - Keep lighting consistent

2. **Calibrate colors**
   ```bash
   python color_calibration.py
   ```
   - Adjust HSV thresholds for your lighting
   - See `TROUBLESHOOTING.md` for details

3. **Check color distribution**
   - Look at the output after scanning
   - Each color should appear exactly 9 times
   - If not, lighting or calibration issue

### Colors Detected Wrong

Try the color calibration tool:

```bash
python color_calibration.py
```

This lets you adjust HSV thresholds for your specific lighting conditions.

Common issues:
- **Orange detected as Red**: Lighting too dim or wrong H thresholds
- **Yellow detected as White**: Glare or wrong S threshold
- **White detected as Yellow**: Shadows or wrong V threshold

### Cube Won't Solve (But Colors Are Right)

**Cause**: Wrong orientation during scanning

**Solution**: Make sure you follow the edge orientation instructions exactly:
- Face 1 (White): Green edge at BOTTOM
- Faces 2-6: Follow the specific edge instructions for each

The edge orientation is critical for the solver to understand the cube's configuration.

### Tips for Best Results

1. **Lighting**
   - Natural daylight works best
   - Avoid direct spotlights (causes glare)
   - Use diffuse lighting if indoors

2. **Cube Position**
   - Keep cube at consistent distance
   - Center it in the grid
   - Don't move cube between faces

3. **Scanning**
   - Wait for green progress bar to fill
   - If colors flicker, hold steadier
   - If wrong face detected, press 'r' to restart

4. **Test First**
   - Try scanning a solved cube first
   - Should give 0-2 moves as solution
   - If not, adjust lighting or calibrate colors

## Additional Tools

### color_calibration.py
Interactive tool to find correct HSV values for your lighting.

```bash
python color_calibration.py
```

Press keys to load presets:
- **W** - White
- **Y** - Yellow
- **G** - Green
- **B** - Blue
- **O** - Orange
- **R** - Red

Adjust sliders until only that color is highlighted, then note the values.

## Understanding the Output

### v5 Output Format

```
Step 1:
  Hold: Green facing you, White on top
  Turn FRONT (facing you) (Green) Clockwise (right)
  [F]
```

Breaking it down:
- **Hold**: How to orient the cube before the move
- **Turn**: Which face to turn
- **Direction**: Which way to turn it
- **[F]**: Standard notation for reference

### Standard Notation (Advanced)

If you're comfortable with cube notation:
- **F** = Front clockwise
- **R** = Right clockwise
- **U** = Top clockwise
- **F'** = Front counter-clockwise
- **R2** = Right 180°

The condensed notation is shown at the bottom of the solution.

## Files in This Project

- **main_v5.py** - Recommended version with orientation instructions
- **main_v4.py** - Solid version without orientation help
- **main_v3.py** - Has Lab re-classification issues
- **main_v2.py** - Basic fix only
- **main.py** - Original (has bugs)
- **color_calibration.py** - HSV threshold tuning tool
- **requirements.txt** - Python dependencies
- **SOLUTION_FORMAT_GUIDE.md** - Detailed solution format explanation
- **TROUBLESHOOTING.md** - Comprehensive troubleshooting guide
- **SCANNING_GUIDE.md** - Cube orientation details

## How It Works

1. **Scanning**: Uses webcam to detect cube colors via HSV color space
2. **Orientation**: Guides you through scanning in Kociemba order (U,R,F,D,L,B)
3. **State Building**: Constructs 54-sticker cube state string
4. **Solving**: Uses Kociemba algorithm to find optimal solution
5. **Formatting**: Converts moves to physical orientation instructions

## Support

If you're still having issues after trying the troubleshooting guide:

1. Check `TROUBLESHOOTING.md` for detailed solutions
2. Try `color_calibration.py` to tune HSV thresholds
3. Test with a solved cube first
4. Ensure cube is physically solvable (no moved stickers)

## License

Free to use and modify.

## Credits

- Kociemba algorithm: Herbert Kociemba
- Python implementation: [kociemba](https://github.com/muodov/kociemba) package

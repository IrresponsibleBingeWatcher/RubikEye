# Rubik's Cube Solver - Troubleshooting Guide

## The Problem You're Experiencing

Your cube was scanned correctly (right faces, right order), but the solver says the cube state is "invalid". This happens when the color distribution is wrong.

## Root Cause Analysis

Looking at your error output, the issue is **color detection accuracy**. The Lab-based color re-classification in v3 was making things WORSE instead of better, incorrectly reassigning colors.

## Solution: Use main_v4.py

**main_v4.py** removes the problematic Lab-space re-classification and uses only HSV color detection. This should be more reliable.

### Key Changes in v4:
1. ✓ Removed Lab color space re-classification
2. ✓ Uses only HSV thresholds for color detection
3. ✓ Still accounts for camera mirror flip
4. ✓ Better debugging output (shows color distribution)
5. ✓ Validates cube string length

## How to Use main_v4.py

```bash
python main_v4.py
```

After scanning all 6 faces, check the output:

```
Color distribution check:
  U: 9 stickers (should be 9) ✓
  R: 9 stickers (should be 9) ✓
  F: 9 stickers (should be 9) ✓
  D: 9 stickers (should be 9) ✓
  L: 9 stickers (should be 9) ✓
  B: 9 stickers (should be 9) ✓
```

**If you see anything other than 9 for each color**, you have a color detection problem.

## Color Detection Issues

### Symptoms:
- Some colors detected as others (e.g., orange → red, yellow → white)
- Color counts not equal to 9 for each
- "Invalid cube state" error

### Causes:
1. **Poor lighting** - Most common!
   - Glare on white/yellow stickers
   - Shadows making colors darker
   - Inconsistent lighting across scans

2. **HSV thresholds not tuned** for your lighting
   - Default values work for "average" conditions
   - Your lighting might be different

### Solutions:

#### Solution 1: Improve Lighting
- Use **natural daylight** (best option)
- Or use multiple diffuse light sources
- Avoid direct spotlights (causes glare)
- Avoid scanning in shadows
- Keep lighting **consistent** across all 6 faces

#### Solution 2: Calibrate Colors
Use the **color_calibration.py** tool:

```bash
python color_calibration.py
```

This opens a window with sliders where you can:
1. Point camera at each cube color
2. Adjust HSV sliders until only that color is highlighted
3. Write down the values
4. Update the HSV thresholds in main_v4.py

**Example: Adjusting for your lighting**

If orange keeps being detected as red:
1. Run color_calibration.py
2. Press 'o' to load orange preset
3. Point camera at orange sticker
4. Adjust H_Low and H_High until only orange is highlighted
5. Write down the values (e.g., H: 8-24)
6. Update main_v4.py line ~59:
   ```python
   if 8 <= h < 24: return 'orange'  # Adjusted from 10-22
   ```

## The Mirror Flip Issue

The code DOES account for the horizontal flip:
```python
# In solve() method, line ~200:
for j in range(2, -1, -1):  # Reads right-to-left
```

This is correct and shouldn't be changed.

## Orientation Issues

Even with correct colors, orientation matters!

### Critical Rules:
1. **Face 1 (White/U)**: Green edge at BOTTOM of camera view
2. **Faces 2-3-4-5-6**: Follow the on-screen instructions EXACTLY
3. **"Rotate right"** means clockwise when viewed from above
4. **"White at top"** means the white edge of that face should be at the top of your camera view

### Testing Orientation:

Try with a **solved cube** first:
- If a solved cube doesn't solve (0 moves), orientation is wrong
- If a solved cube solves correctly, orientation is right

## Systematic Debugging Approach

1. **Test with solved cube**
   ```bash
   python main_v4.py
   ```
   - Scan a fully solved cube
   - Expected output: Solution with 0-2 moves
   - If it says "invalid", you have detection or orientation issues

2. **Check color distribution**
   - Look at the "Color distribution check" in output
   - Each color should appear exactly 9 times
   - If not → lighting/calibration issue

3. **Calibrate colors if needed**
   ```bash
   python color_calibration.py
   ```
   - Adjust HSV thresholds for your lighting
   - Update values in main_v4.py

4. **Verify orientation**
   - Double-check you're following the instructions exactly
   - The edge orientations are crucial
   - When in doubt, start over with 'r' key

## Common Mistakes

1. **Not following edge orientation**
   - "White at top" means the WHITE EDGE, not any random edge
   - This is the most common mistake

2. **Inconsistent lighting**
   - Different lighting when scanning different faces
   - Move around = colors change

3. **Glare on white/yellow**
   - Makes them look the same
   - Solution: Adjust cube angle slightly

4. **Moving too fast**
   - Wait for the green progress bar to fill completely
   - If colors are flickering, hold steadier

## Advanced: Manual HSV Tuning

Edit main_v4.py around line 54-62:

```python
def get_color_name(self, hsv_pixel):
    h, s, v = hsv_pixel
    
    # White check (Low saturation)
    if s < 70: return 'white'  # Adjust 70 if needed
    
    # Adjust these ranges based on color_calibration.py
    if 22 <= h < 45: return 'yellow'
    if 45 <= h < 90: return 'green'
    if 95 <= h < 140: return 'blue'
    if 10 <= h < 22: return 'orange'
    if h < 10 or h >= 160: return 'red'
```

## Still Not Working?

If after all this it still doesn't work:

1. **Check your cube is solvable**
   - Stickers might be peeled/swapped
   - Try an online cube solver manually

2. **Try a different cube**
   - Some cubes have ambiguous colors
   - Stickerless cubes sometimes work better

3. **Try different camera position**
   - Closer/farther
   - Different angle
   - Different background

4. **Last resort: Manual entry**
   - Some online tools let you manually click colors
   - Use those if automated detection fails

## Version Summary

- **main.py** (original): Mirror flip bug, no orientation guidance
- **main_v2.py**: Fixed mirror flip
- **main_v3.py**: Added orientation guidance, but Lab re-classification caused problems
- **main_v4.py**: Removed Lab re-classification, cleaner HSV detection ← **USE THIS**
- **color_calibration.py**: Tool to find correct HSV values for your lighting

Good luck! The key is getting the colors detected accurately. Once that works, the solver should work reliably.

# Rubik's Cube Scanning Guide

## The Problem with v2

The issue wasn't just the mirror flip - it was that **cube orientation matters**!

When Kociemba solves a cube, it expects the faces to be encoded in a very specific way:
- Not just "which face is which color"
- But "how are the faces oriented relative to each other"

## Why Your Scan Failed

You scanned the faces in this order: Green, Red, Blue, Orange, White, Yellow

But Kociemba expects: White (U), Red (R), Green (F), Yellow (D), Orange (L), Blue (B)

More importantly, **each face needs to be oriented correctly**. For example:
- When scanning White (U), which edge aligns with Green (F)?
- When scanning Red (R), which edge aligns with White (U)?

If these relationships aren't preserved, the cube state is "impossible" to solve.

## How v3 Fixes This

**main_v3.py** guides you through a very specific scanning sequence:

### Step 1: UP (White center)
```
      [white face pointing at camera]
      
      Green edge at BOTTOM of camera view
      (This sets the reference orientation)
```

### Step 2: RIGHT (Red center)
```
Rotate cube RIGHT (clockwise when viewed from above)
      
      [red face pointing at camera]
      
      White edge at TOP of camera view
      (This maintains the "up" reference)
```

### Step 3: FRONT (Green center)
```
Rotate cube RIGHT again
      
      [green face pointing at camera]
      
      White edge at TOP of camera view
```

### Step 4: DOWN (Yellow center)
```
Rotate cube RIGHT again, then flip ENTIRE cube upside down
      
      [yellow face pointing at camera]
      
      Green edge at TOP of camera view
      (Yellow is now the "down" face)
```

### Step 5: LEFT (Orange center)
```
Rotate cube RIGHT
      
      [orange face pointing at camera]
      
      White edge at TOP of camera view
```

### Step 6: BACK (Blue center)
```
Rotate cube RIGHT again
      
      [blue face pointing at camera]
      
      White edge at TOP of camera view
```

## Key Differences in v3

1. **Validates center color**: Won't capture unless the correct center color is detected
2. **Step-by-step guidance**: Shows exactly which face to scan next
3. **Visual progress**: Clear indicators of which faces are captured
4. **Error messages**: Tells you if you're showing the wrong face
5. **Restart option**: Press 'r' to start over if you make a mistake

## Tips for Success

1. **Good lighting is critical**
   - Avoid glare on the cube
   - Natural daylight works best
   - Avoid shadows

2. **Hold cube steady**
   - Keep it at the same distance from camera
   - Center it in the grid
   - Wait for the green progress bar to fill

3. **Follow orientation exactly**
   - Pay attention to which edge should be at the top/bottom
   - The edge orientation is what makes the cube solvable

4. **If it fails**
   - Press 'r' to restart
   - Double-check your cube hasn't been tampered with (moved stickers)
   - Try better lighting

## Technical Note

The v3 version:
- Captures faces in Kociemba order (U, R, F, D, L, B)
- Reverses column order when reading (to account for mirror flip)
- Uses CIELAB color space for accurate color matching
- Validates that the center sticker matches expectations

This ensures that the cube state is encoded correctly for the solver.

# main_v5.py - Solution with Physical Orientation Instructions

## What's New in v5?

**Physical cube holding instructions** for each move! Instead of just saying "F clockwise", it tells you:
- How to hold the cube (which color faces you, which color on top)
- Which face to turn
- Which direction to turn it

## Example Output

Here's what a solution looks like in v5:

```
======================================================================
SOLUTION - FOLLOW THESE STEPS
======================================================================

Starting position: Green facing you, White on top

Step 1:
  Hold: Green facing you, White on top
  Turn FRONT (facing you) (Green) Clockwise (right)
  [F]

Step 2:
  Hold: Green facing you, White on top
  Turn RIGHT (Red) Clockwise (right)
  [R]

Step 3:
  Hold: Green facing you, White on top
  Turn TOP (White) Counter-Clockwise (left)
  [U']

Step 4:
  Hold: Red facing you, White on top
  Turn RIGHT (Red) Counter-Clockwise (left)
  [R']

Step 5:
  Hold: Green facing you, White on top
  Turn TOP (White) Clockwise (right)
  [U]

Step 6:
  Hold: Green facing you, White on top
  Turn FRONT (facing you) (Green) Counter-Clockwise (left)
  [F']

Step 7:
  Hold: Red facing you, White on top
  Turn RIGHT (Red) Clockwise (right)
  [R]

Step 8:
  Hold: Green facing you, White on top
  Turn TOP (White) Counter-Clockwise (left)
  [U']

Step 9:
  Hold: Red facing you, White on top
  Turn RIGHT (Red) Counter-Clockwise (left)
  [R']

======================================================================
✓ Cube should now be solved!
======================================================================

Condensed notation:
F R U' R' U F' R U' R'
```

## How to Use

1. **Start with the correct orientation:**
   - Green facing you
   - White on top

2. **For each step:**
   - First, reorient the cube as instructed
   - Then turn the specified face in the specified direction
   - Keep other faces stable

3. **Understanding the directions:**
   - **Clockwise (right)**: Turn the face like turning a doorknob to the right
   - **Counter-Clockwise (left)**: Turn the face like turning a doorknob to the left
   - **180° (half turn)**: Turn the face halfway around

## Face Positions Explained

When holding the cube with Green facing you and White on top:

- **FRONT (Green)**: The face facing you
- **BACK (Blue)**: The face away from you
- **TOP (White)**: The face on top
- **BOTTOM (Yellow)**: The face on bottom
- **LEFT (Orange)**: The face on your left
- **RIGHT (Red)**: The face on your right

## Tips for Following the Solution

1. **Take your time**
   - Do one move at a time
   - Check your orientation before each move
   - Don't rush

2. **If you get lost**
   - Go back to: Green facing you, White on top
   - Find where you are in the sequence
   - Continue from there

3. **Practice with a solved cube first**
   - Scramble it just a little bit
   - Follow the solution steps
   - Get comfortable with the notation

4. **Understanding orientation changes**
   - Some moves require you to rotate the whole cube
   - For example: "Hold: Red facing you, White on top"
   - This means rotate the entire cube so Red is now facing you

## Common Moves Explained

### F (Front Clockwise)
- Hold: Green facing you, White on top
- Turn the Green face clockwise
- Imagine turning a doorknob to the right

### R (Right Clockwise)
- Hold: Green facing you, White on top
- Turn the Red face (right side) clockwise
- Turn it away from you at the top

### U' (Top Counter-Clockwise)
- Hold: Green facing you, White on top
- Turn the White face counter-clockwise
- Turn it to the left

### R' (Right Counter-Clockwise)
- Hold: Green facing you, White on top
- Turn the Red face counter-clockwise
- Turn it toward you at the top

## Comparison: Old vs New Format

### Old Format (v4 and earlier):
```
1. TOP (White) -> Clockwise
2. RIGHT (Red) -> Counter-Clockwise
3. FRONT (Green) -> 180 degrees (Twice)
```

**Problem**: You have to figure out yourself which color is which face based on current cube orientation.

### New Format (v5):
```
Step 1:
  Hold: Green facing you, White on top
  Turn TOP (White) Clockwise (right)
  [U]

Step 2:
  Hold: Red facing you, White on top
  Turn RIGHT (Red) Counter-Clockwise (left)
  [R']

Step 3:
  Hold: Green facing you, White on top
  Turn FRONT (facing you) (Green) 180° (half turn)
  [F2]
```

**Benefit**: Each step tells you exactly how to hold the cube before making the move!

## Why This Matters

Rubik's cube notation assumes you know the "standard orientation" and can track it in your head as you make moves. For beginners, this is confusing because:

1. After a few moves, you lose track of which face is which
2. "Front" means different things at different points in the solution
3. You have to mentally rotate the cube to understand what "R" means

With v5, **you don't need to track anything mentally**. Just follow the holding instructions for each step!

## Advanced: Understanding Notation

If you want to learn standard notation:

- **Letters** = Faces (U, D, L, R, F, B)
- **No modifier** = Clockwise (e.g., F)
- **' (prime)** = Counter-clockwise (e.g., R')
- **2** = 180° turn (e.g., U2)

Once you're comfortable, you can just follow the condensed notation at the bottom of the output.

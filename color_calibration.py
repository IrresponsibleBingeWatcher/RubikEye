import cv2
import numpy as np

"""
Color Calibration Tool for Rubik's Cube Scanner
This helps you find the right HSV thresholds for your lighting conditions.
"""

def nothing(x):
    pass

def main():
    cap = cv2.VideoCapture(0)
    
    # Create window with trackbars
    cv2.namedWindow('Color Calibration')
    
    # Create trackbars for HSV adjustment
    cv2.createTrackbar('H_Low', 'Color Calibration', 0, 180, nothing)
    cv2.createTrackbar('H_High', 'Color Calibration', 180, 180, nothing)
    cv2.createTrackbar('S_Low', 'Color Calibration', 0, 255, nothing)
    cv2.createTrackbar('S_High', 'Color Calibration', 255, 255, nothing)
    cv2.createTrackbar('V_Low', 'Color Calibration', 0, 255, nothing)
    cv2.createTrackbar('V_High', 'Color Calibration', 255, 255, nothing)
    
    # Default values for white detection
    cv2.setTrackbarPos('H_Low', 'Color Calibration', 0)
    cv2.setTrackbarPos('H_High', 'Color Calibration', 180)
    cv2.setTrackbarPos('S_Low', 'Color Calibration', 0)
    cv2.setTrackbarPos('S_High', 'Color Calibration', 70)
    cv2.setTrackbarPos('V_Low', 'Color Calibration', 150)
    cv2.setTrackbarPos('V_High', 'Color Calibration', 255)
    
    print("="*70)
    print("COLOR CALIBRATION TOOL")
    print("="*70)
    print("\nInstructions:")
    print("1. Point camera at a Rubik's cube sticker")
    print("2. Adjust trackbars until only that color is highlighted in white")
    print("3. Write down the HSV values for each color")
    print("\nPreset colors (press key to load):")
    print("  w - White   y - Yellow   g - Green")
    print("  b - Blue    o - Orange   r - Red")
    print("\nPress 'q' to quit")
    print("="*70)
    
    # Preset values
    presets = {
        'w': {'name': 'White', 'h': (0, 180), 's': (0, 70), 'v': (150, 255)},
        'y': {'name': 'Yellow', 'h': (22, 45), 's': (100, 255), 'v': (100, 255)},
        'g': {'name': 'Green', 'h': (45, 90), 's': (40, 255), 'v': (40, 255)},
        'b': {'name': 'Blue', 'h': (95, 140), 's': (100, 255), 'v': (60, 255)},
        'o': {'name': 'Orange', 'h': (10, 22), 's': (100, 255), 'v': (100, 255)},
        'r': {'name': 'Red', 'h': (0, 10), 's': (100, 255), 'v': (100, 255)}
    }
    
    current_preset = 'w'
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get trackbar values
        h_low = cv2.getTrackbarPos('H_Low', 'Color Calibration')
        h_high = cv2.getTrackbarPos('H_High', 'Color Calibration')
        s_low = cv2.getTrackbarPos('S_Low', 'Color Calibration')
        s_high = cv2.getTrackbarPos('S_High', 'Color Calibration')
        v_low = cv2.getTrackbarPos('V_Low', 'Color Calibration')
        v_high = cv2.getTrackbarPos('V_High', 'Color Calibration')
        
        # Create mask
        lower = np.array([h_low, s_low, v_low])
        upper = np.array([h_high, s_high, v_high])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Apply mask
        result = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Show current values on screen
        cv2.putText(frame, f"H: {h_low}-{h_high}  S: {s_low}-{s_high}  V: {v_low}-{v_high}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Current: {presets[current_preset]['name']}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Sample center pixel color
        h, w = frame.shape[:2]
        center_hsv = hsv[h//2, w//2]
        cv2.circle(frame, (w//2, h//2), 20, (0, 255, 0), 2)
        cv2.putText(frame, f"Center HSV: {center_hsv}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Stack images
        combined = np.hstack([frame, result])
        cv2.imshow('Color Calibration', combined)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key in [ord(k) for k in presets.keys()]:
            # Load preset
            key_char = chr(key)
            current_preset = key_char
            preset = presets[key_char]
            print(f"\nLoaded preset: {preset['name']}")
            cv2.setTrackbarPos('H_Low', 'Color Calibration', preset['h'][0])
            cv2.setTrackbarPos('H_High', 'Color Calibration', preset['h'][1])
            cv2.setTrackbarPos('S_Low', 'Color Calibration', preset['s'][0])
            cv2.setTrackbarPos('S_High', 'Color Calibration', preset['s'][1])
            cv2.setTrackbarPos('V_Low', 'Color Calibration', preset['v'][0])
            cv2.setTrackbarPos('V_High', 'Color Calibration', preset['v'][1])
        elif key == ord('p'):
            # Print current values
            print(f"\nCurrent values:")
            print(f"  H: [{h_low}, {h_high}]")
            print(f"  S: [{s_low}, {s_high}]")
            print(f"  V: [{v_low}, {v_high}]")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

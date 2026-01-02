import cv2
import numpy as np
import kociemba
import sys
import time

class RubikSolver:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Grid parameters (adjust based on camera resolution)
        self.box_size = 50
        self.gap = 10
        self.start_x = (self.width - (3 * self.box_size + 2 * self.gap)) // 2
        self.start_y = (self.height - (3 * self.box_size + 2 * self.gap)) // 2

        # State - now we store faces in Kociemba order
        self.captured_faces = {}  # Keys: 'U', 'R', 'F', 'D', 'L', 'B'
        self.scan_sequence = ['U', 'R', 'F', 'D', 'L', 'B']
        self.current_scan_index = 0
        
        # Face descriptions
        self.face_descriptions = {
            'U': 'UP (White center) - Green edge at BOTTOM of camera view',
            'R': 'RIGHT (Red center) - White edge at TOP of camera view',
            'F': 'FRONT (Green center) - White edge at TOP of camera view',
            'D': 'DOWN (Yellow center) - Green edge at TOP of camera view',
            'L': 'LEFT (Orange center) - White edge at TOP of camera view',
            'B': 'BACK (Blue center) - White edge at TOP of camera view'
        }
        
        # Expected center colors for validation
        self.expected_centers = {
            'U': 'white',
            'R': 'red',
            'F': 'green',
            'D': 'yellow',
            'L': 'orange',
            'B': 'blue'
        }
        
        # Stability tracking for auto-capture
        self.last_grid_names = None
        self.stability_start_time = None
        self.STABILITY_DURATION = 3.0
        
        self.bgr_display = {
            'white': (255, 255, 255),
            'yellow': (0, 255, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'orange': (0, 165, 255),
            'red': (0, 0, 255),
            'unknown': (128, 128, 128)
        }

    def get_color_name(self, hsv_pixel):
        h, s, v = hsv_pixel
        
        # White check (Low saturation)
        if s < 70: 
            return 'white'
        
        # Hue based checks with refined ranges
        if 22 <= h < 45: return 'yellow'
        if 45 <= h < 90: return 'green'
        if 95 <= h < 140: return 'blue'
        if 10 <= h < 22: return 'orange'
        if h < 10 or h >= 160: return 'red'
        
        return 'unknown'

    def draw_grid_and_detect(self, frame):
        grid_names = [['' for _ in range(3)] for _ in range(3)]
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for i in range(3):
            for j in range(3):
                x = self.start_x + j * (self.box_size + self.gap)
                y = self.start_y + i * (self.box_size + self.gap)
                
                # Sample from 4 points to avoid glare
                roi_size = 8
                margin = 6
                half_box = self.box_size // 2
                half_roi = roi_size // 2
                
                rois_coords = [
                    (x + half_box - half_roi, y + margin),
                    (x + half_box - half_roi, y + self.box_size - margin - roi_size),
                    (x + margin, y + half_box - half_roi),
                    (x + self.box_size - margin - roi_size, y + half_box - half_roi)
                ]
                
                hsv_samples = []
                
                for rx, ry in rois_coords:
                    roi_hsv = hsv_frame[ry:ry+roi_size, rx:rx+roi_size]
                    if roi_hsv.size > 0:
                        hsv_samples.append(np.mean(roi_hsv, axis=(0,1)))
                        cv2.rectangle(frame, (rx, ry), (rx+roi_size, ry+roi_size), (50, 50, 50), 1)

                if hsv_samples:
                    avg_hsv = np.mean(hsv_samples, axis=0)
                    color_name = self.get_color_name(avg_hsv)
                    grid_names[i][j] = color_name
                    
                    display_color = self.bgr_display.get(color_name, (128, 128, 128))
                    cv2.rectangle(frame, (x, y), (x + self.box_size, y + self.box_size), display_color, 2)
                    cv2.circle(frame, (x + self.box_size//2, y + self.box_size//2), 5, display_color, -1)
                
        return grid_names

    def format_solution(self, solution_str):
        moves = solution_str.split()
        instructions = []
        
        map_face = {
            'U': 'TOP (White)', 'D': 'BOTTOM (Yellow)',
            'L': 'LEFT (Orange)', 'R': 'RIGHT (Red)',
            'F': 'FRONT (Green)', 'B': 'BACK (Blue)'
        }
        
        for move in moves:
            face = move[0]
            action = move[1:] if len(move) > 1 else ""
            face_name = map_face.get(face, face)
            
            if action == "'":
                desc = "Counter-Clockwise"
            elif action == "2":
                desc = "180 degrees (Twice)"
            else:
                desc = "Clockwise"
                
            instructions.append(f"{face_name} -> {desc}")
            
        return instructions

    def run(self):
        print("Starting Rubik's Cube Solver...")
        print("\n" + "="*70)
        print("CUBE SCANNING INSTRUCTIONS")
        print("="*70)
        print("\nYou will scan 6 faces with SPECIFIC orientations:")
        print()
        print("1. UP (White) - Green edge at BOTTOM of screen")
        print("2. RIGHT (Red) - Rotate right, White edge at TOP")
        print("3. FRONT (Green) - Rotate right, White edge at TOP")
        print("4. DOWN (Yellow) - Rotate right, flip cube, Green edge at TOP")
        print("5. LEFT (Orange) - Rotate right, White edge at TOP")
        print("6. BACK (Blue) - Rotate right, White edge at TOP")
        print()
        print("Hold steady for 3 seconds to capture. Press 'q' to quit, 'r' to restart.")
        print("="*70)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            
            if self.current_scan_index < 6:
                current_face = self.scan_sequence[self.current_scan_index]
                expected_center = self.expected_centers[current_face]
                face_desc = self.face_descriptions[current_face]
                
                cv2.putText(frame, f"Step {self.current_scan_index + 1}/6: {face_desc}", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                y_offset = 70
                for i, face in enumerate(self.scan_sequence):
                    if i < self.current_scan_index:
                        status = "[X]"
                        color = (0, 255, 0)
                    elif i == self.current_scan_index:
                        status = "[>]"
                        color = (0, 255, 255)
                    else:
                        status = "[ ]"
                        color = (128, 128, 128)
                    
                    text = f"{status} {face}: {self.expected_centers[face].capitalize()}"
                    cv2.putText(frame, text, (20, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.2, color, 2)
                    y_offset += 25

                current_names = self.draw_grid_and_detect(frame)
                center_name = current_names[1][1]
                
                if center_name == expected_center:
                    if current_names == self.last_grid_names:
                        if self.stability_start_time is None:
                            self.stability_start_time = time.time()
                    else:
                        self.stability_start_time = time.time()
                        self.last_grid_names = current_names
                    
                    elapsed = time.time() - self.stability_start_time
                    bar_width = int(min(elapsed / self.STABILITY_DURATION, 1.0) * 300)
                    cv2.rectangle(frame, (20, self.height - 60), (20 + bar_width, self.height - 40), (0, 255, 0), -1)
                    cv2.rectangle(frame, (20, self.height - 60), (320, self.height - 40), (255, 255, 255), 2)
                    cv2.putText(frame, "Capturing...", (325, self.height - 42), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 2)
                    
                    if elapsed >= self.STABILITY_DURATION:
                        self.captured_faces[current_face] = current_names
                        print(f"\n✓ Captured {current_face}: {expected_center.capitalize()}")
                        print(f"  Detected: {current_names}")
                        self.current_scan_index += 1
                        self.stability_start_time = None
                        self.last_grid_names = None
                        time.sleep(0.5)
                elif center_name != 'unknown':
                    cv2.putText(frame, f"Wrong! Need {expected_center}, got {center_name}", 
                               (20, self.height - 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                    self.stability_start_time = None
                    self.last_grid_names = None
                else:
                    self.stability_start_time = None
                    self.last_grid_names = None
                
            else:
                cv2.putText(frame, "All Faces Captured! Processing...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Rubik's Solver", frame)
                cv2.waitKey(500) 
                break

            cv2.imshow("Rubik's Solver", frame)
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                self.cap.release()
                cv2.destroyAllWindows()
                return
            elif key == ord('r'):
                self.captured_faces = {}
                self.current_scan_index = 0
                self.stability_start_time = None
                self.last_grid_names = None
                print("\n--- Restarting scan ---")

        self.cap.release()
        cv2.destroyAllWindows()
        
        if len(self.captured_faces) == 6:
            self.solve()

    def solve(self):
        print("\n" + "="*70)
        print("Building Cube State...")
        print("="*70)
        
        # Map color names to Kociemba face letters
        color_to_face = {
            'white': 'U',
            'red': 'R',
            'green': 'F',
            'yellow': 'D',
            'orange': 'L',
            'blue': 'B'
        }
        
        cube_string = ""
        
        # Process each face in Kociemba order: U, R, F, D, L, B
        for face in self.scan_sequence:
            grid_names = self.captured_faces[face]
            
            print(f"\n{face} ({self.expected_centers[face].capitalize()}):")
            for i in range(3):
                row = []
                # Reverse column order to account for horizontal flip
                for j in range(2, -1, -1):
                    color = grid_names[i][j]
                    if color in color_to_face:
                        cube_string += color_to_face[color]
                        row.append(color)
                    else:
                        print(f"  ERROR: Unknown color '{color}' at position ({i}, {j})")
                        return
                print(f"  {row}")

        print(f"\n{'='*70}")
        print(f"Cube String: {cube_string}")
        print(f"Length: {len(cube_string)} (should be 54)")
        print(f"{'='*70}")
        
        if len(cube_string) != 54:
            print("\nERROR: Cube string is wrong length!")
            return
        
        try:
            print("\nSolving...")
            solution = kociemba.solve(cube_string)
            print(f"\n✓ SUCCESS! Solution found!")
            print(f"Moves: {solution}")
            
            steps = self.format_solution(solution)
            print("\n" + "="*70)
            print("SOLUTION STEPS")
            print("="*70)
            for i, step in enumerate(steps):
                print(f"{i+1:2d}. {step}")
            print("="*70)
                
        except Exception as e:
            print("\n" + "="*70)
            print("✗ ERROR: Could not solve")
            print("="*70)
            print("Common causes:")
            print("  • Lighting issues (try better/different lighting)")
            print("  • Wrong cube orientation during scanning")
            print("  • Color detection errors (adjust HSV thresholds)")
            print("  • Physically impossible cube (stickers moved)")
            print(f"\nDetails: {e}")
            print("="*70)
            
            # Debug: Count each color
            print("\nColor distribution check:")
            for color in ['U', 'R', 'F', 'D', 'L', 'B']:
                count = cube_string.count(color)
                print(f"  {color}: {count} stickers (should be 9)")

if __name__ == "__main__":
    solver = RubikSolver()
    solver.run()

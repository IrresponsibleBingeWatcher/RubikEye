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
        # Stores tuple (grid_names, grid_bgr) keyed by face position
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
        self.STABILITY_DURATION = 3.0 # Seconds of consistent frames before capture
        
        # Color definitions (HSV Ranges) - ONLY FOR UI FEEDBACK
        self.colors = {
            'white':  ([0, 0, 150], [180, 60, 255]),
            'yellow': ([20, 100, 100], [40, 255, 255]),
            'green':  ([40, 40, 40], [90, 255, 255]),
            'blue':   ([95, 100, 60], [130, 255, 255]),
            'orange': ([5, 100, 100], [20, 255, 255]),
            'red1':   ([0, 100, 100], [5, 255, 255]),
            'red2':   ([170, 100, 100], [180, 255, 255])
        }
        
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
        
        # Hue based checks with refined ranges to prevent flickering
        if 22 <= h < 45: return 'yellow'
        if 45 <= h < 90: return 'green'
        if 95 <= h < 140: return 'blue'
        if 10 <= h < 22: return 'orange'
        if h < 10 or h >= 160: return 'red'
        
        return 'unknown'

    def draw_grid_and_detect(self, frame):
        # returns (grid_names, grid_bgr)
        grid_names = [['' for _ in range(3)] for _ in range(3)]
        grid_bgr = np.zeros((3, 3, 3), dtype=np.uint8)
        
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for i in range(3):
            for j in range(3):
                x = self.start_x + j * (self.box_size + self.gap)
                y = self.start_y + i * (self.box_size + self.gap)
                
                # ROI for color detection (4 sides to avoid center glare)
                roi_size = 8
                margin = 6
                
                # Define offsets for 4 ROIs: Top, Bottom, Left, Right
                half_box = self.box_size // 2
                half_roi = roi_size // 2
                
                rois_coords = [
                    (x + half_box - half_roi, y + margin),                            # Top
                    (x + half_box - half_roi, y + self.box_size - margin - roi_size), # Bottom
                    (x + margin, y + half_box - half_roi),                            # Left
                    (x + self.box_size - margin - roi_size, y + half_box - half_roi)  # Right
                ]
                
                hsv_samples = []
                bgr_samples = []
                
                for rx, ry in rois_coords:
                    roi_hsv = hsv_frame[ry:ry+roi_size, rx:rx+roi_size]
                    roi_bgr = frame[ry:ry+roi_size, rx:rx+roi_size]
                    
                    if roi_hsv.size > 0:
                        hsv_samples.append(np.mean(roi_hsv, axis=(0,1)))
                        bgr_samples.append(np.mean(roi_bgr, axis=(0,1)))
                        # Visualize sampling points (optional, small dots)
                        cv2.rectangle(frame, (rx, ry), (rx+roi_size, ry+roi_size), (50, 50, 50), 1)

                # Average color from samples
                if hsv_samples:
                    avg_hsv = np.mean(hsv_samples, axis=0)
                    avg_bgr = np.mean(bgr_samples, axis=0)
                    
                    color_name = self.get_color_name(avg_hsv)
                    grid_names[i][j] = color_name
                    grid_bgr[i][j] = avg_bgr
                    
                    # Draw box
                    display_color = self.bgr_display.get(color_name, (128, 128, 128))
                    cv2.rectangle(frame, (x, y), (x + self.box_size, y + self.box_size), display_color, 2)
                    
                    # Draw small filled circle in center to show detected color
                    cv2.circle(frame, (x + self.box_size//2, y + self.box_size//2), 5, display_color, -1)
                
        return grid_names, grid_bgr

    def format_solution(self, solution_str):
        # Expand simplified notation to human readable
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
        print("IMPORTANT: Cube Orientation Instructions")
        print("="*70)
        print("You will scan 6 faces in this EXACT order and orientation:")
        print()
        print("1. UP (White center)")
        print("   - White face pointing at camera")
        print("   - Green edge at the BOTTOM of your camera view")
        print()
        print("2. RIGHT (Red center)")
        print("   - Rotate cube RIGHT (clockwise from above)")
        print("   - Red face pointing at camera")
        print("   - Keep White edge at TOP of camera view")
        print()
        print("3. FRONT (Green center)")
        print("   - Rotate cube RIGHT again")
        print("   - Green face pointing at camera")
        print("   - Keep White edge at TOP of camera view")
        print()
        print("4. DOWN (Yellow center)")
        print("   - Rotate cube RIGHT again")
        print("   - Then flip ENTIRE cube upside down")
        print("   - Yellow face pointing at camera")
        print("   - Keep Green edge at TOP of camera view")
        print()
        print("5. LEFT (Orange center)")
        print("   - Rotate cube RIGHT")
        print("   - Orange face pointing at camera")
        print("   - Keep White edge at TOP of camera view")
        print()
        print("6. BACK (Blue center)")
        print("   - Rotate cube RIGHT again")
        print("   - Blue face pointing at camera")
        print("   - Keep White edge at TOP of camera view")
        print()
        print("Hold each face steady for 3 seconds to auto-capture.")
        print("Press 'q' to quit, 'r' to restart scanning.")
        print("="*70)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1) # Mirror view for easier interaction
            
            if self.current_scan_index < 6:
                # Detection Phase
                current_face = self.scan_sequence[self.current_scan_index]
                expected_center = self.expected_centers[current_face]
                face_desc = self.face_descriptions[current_face]
                
                # Show current instruction
                cv2.putText(frame, f"Step {self.current_scan_index + 1}/6: {face_desc}", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw status of captured faces
                y_offset = 70
                for i, face in enumerate(self.scan_sequence):
                    if i < self.current_scan_index:
                        status = "[X]"
                        color = (0, 255, 0)  # Green for captured
                    elif i == self.current_scan_index:
                        status = "[>]"
                        color = (0, 255, 255)  # Yellow for current
                    else:
                        status = "[ ]"
                        color = (128, 128, 128)  # Gray for pending
                    
                    text = f"{status} {face}: {self.expected_centers[face].capitalize()}"
                    cv2.putText(frame, text, (20, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.2, color, 2)
                    y_offset += 25

                current_names, current_bgr = self.draw_grid_and_detect(frame)
                
                # Stability Check and Auto-Capture
                center_name = current_names[1][1]
                
                # Validate center color
                if center_name == expected_center:
                    # Check if grid names are stable
                    if current_names == self.last_grid_names:
                        if self.stability_start_time is None:
                            self.stability_start_time = time.time()
                    else:
                        self.stability_start_time = time.time()
                        self.last_grid_names = current_names
                    
                    elapsed = time.time() - self.stability_start_time
                    
                    # Draw stability bar
                    bar_width = int(min(elapsed / self.STABILITY_DURATION, 1.0) * 300)
                    cv2.rectangle(frame, (20, self.height - 60), (20 + bar_width, self.height - 40), (0, 255, 0), -1)
                    cv2.rectangle(frame, (20, self.height - 60), (320, self.height - 40), (255, 255, 255), 2)
                    cv2.putText(frame, "Capturing...", (325, self.height - 42), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 2)
                    
                    if elapsed >= self.STABILITY_DURATION:
                        self.captured_faces[current_face] = (current_names, current_bgr)
                        print(f"\n✓ Captured {current_face}: {expected_center.capitalize()}")
                        print(f"  Colors: {current_names}")
                        self.current_scan_index += 1
                        self.stability_start_time = None
                        self.last_grid_names = None
                        time.sleep(0.5)  # Brief pause before next face
                elif center_name != 'unknown':
                    # Wrong center color
                    cv2.putText(frame, f"Wrong face! Need {expected_center}, got {center_name}", 
                               (20, self.height - 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                    self.stability_start_time = None
                    self.last_grid_names = None
                else:
                    self.stability_start_time = None
                    self.last_grid_names = None
                
            else:
                # Solving Phase
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
                # Restart scanning
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
        print("Constructing Cube State...")
        print("="*70)
        
        # 1. Identify Center Colors (References)
        centers_bgr = {}
        for face, (_, grid_bgr) in self.captured_faces.items():
            centers_bgr[face] = grid_bgr[1][1]  # Center piece

        # Helper to convert single BGR to Lab
        def to_lab(bgr_pixel):
            reshaped = np.uint8([[bgr_pixel]])
            lab = cv2.cvtColor(reshaped, cv2.COLOR_BGR2Lab)
            return lab[0][0].astype(int)

        # Convert centers to Lab
        centers_lab = {face: to_lab(bgr) for face, bgr in centers_bgr.items()}
        
        # Map face letters to color names for display
        face_to_color = {
            'U': 'white', 'R': 'red', 'F': 'green',
            'D': 'yellow', 'L': 'orange', 'B': 'blue'
        }
        
        cube_string = ""
        
        print("\nRe-evaluating colors based on relative differences...")
        print("(Accounting for camera mirror flip)")

        # Process faces in Kociemba order: U, R, F, D, L, B
        for face in self.scan_sequence:
            _, grid_bgr = self.captured_faces[face]
            
            print(f"\n{face} ({face_to_color[face].capitalize()}) face:")
            
            for i in range(3):
                row_evaluated = []
                # FIX: Reverse column order to account for horizontal flip
                for j in range(2, -1, -1):
                    pixel_bgr = grid_bgr[i][j]
                    pixel_lab = to_lab(pixel_bgr)
                    
                    # Find closest center
                    min_dist = float('inf')
                    best_match_face = None
                    
                    for center_face, center_lab in centers_lab.items():
                        dist = np.linalg.norm(pixel_lab - center_lab)
                        if dist < min_dist:
                            min_dist = dist
                            best_match_face = center_face
                    
                    cube_string += best_match_face
                    row_evaluated.append(face_to_color[best_match_face])
                
                print(f"  {row_evaluated}")

        print(f"\n{'='*70}")
        print(f"Cube String: {cube_string}")
        print(f"{'='*70}")
        
        try:
            print("\nSolving...")
            solution = kociemba.solve(cube_string)
            print(f"\n✓ Solution found!")
            print(f"Moves: {solution}")
            
            steps = self.format_solution(solution)
            print("\n" + "="*70)
            print("Step-by-Step Solution")
            print("="*70)
            for i, step in enumerate(steps):
                print(f"{i+1:2d}. {step}")
            print("="*70)
                
        except Exception as e:
            print("\n" + "="*70)
            print("✗ Error: Could not find a solution")
            print("="*70)
            print("This usually means:")
            print("  • Colors were scanned incorrectly")
            print("  • Cube orientation was wrong during scanning")
            print("  • Cube is physically unsolvable (e.g., stickers moved)")
            print(f"\nTechnical details: {e}")
            print("="*70)
            print("\nTip: Make sure you followed the orientation instructions exactly!")
            print("     Pay special attention to which edge should be at the")
            print("     top/bottom of your camera view for each face.")

if __name__ == "__main__":
    solver = RubikSolver()
    solver.run()

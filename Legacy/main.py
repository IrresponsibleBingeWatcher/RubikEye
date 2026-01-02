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

        # State
        # Stores tuple (grid_names, grid_bgr) keyed by center color name
        self.captured_map = {} 
        self.expected_centers = ['white', 'red', 'green', 'yellow', 'orange', 'blue']
        
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
        print("\nScanning Instructions:")
        print("1. Scan the first face.")
        print("2. Turn the cube right (from the holder's perspective).")
        print("3. Turn it again right.")
        print("4. Turn it again right.")
        print("5. Turn it again right.")
        print("6. Rotate forward 90 degrees (top).")
        print("7. Rotate forward 180 degrees (bottom).")
        print("\nHold each face steady to register it. Press 'q' to quit.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1) # Mirror view for easier interaction
            
            if len(self.captured_map) < 6:
                # Detection Phase
                cv2.putText(frame, "Scan Faces (Hold Steady)", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Draw status of captured faces
                y_offset = 100
                for color in self.expected_centers:
                    status = "[X]" if color in self.captured_map else "[ ]"
                    text = f"{status} {color.capitalize()}"
                    col_bgr = self.bgr_display.get(color, (255, 255, 255))
                    cv2.putText(frame, text, (20, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.5, col_bgr, 2)
                    y_offset += 30

                current_names, current_bgr = self.draw_grid_and_detect(frame)
                
                # Stability Check and Auto-Capture
                center_name = current_names[1][1]
                
                if center_name != 'unknown':
                    # Check if grid names are stable
                    if current_names == self.last_grid_names:
                        if self.stability_start_time is None:
                            self.stability_start_time = time.time()
                    else:
                        self.stability_start_time = time.time()
                        self.last_grid_names = current_names
                    
                    elapsed = time.time() - self.stability_start_time
                    
                    # Draw stability bar
                    bar_width = int(min(elapsed / self.STABILITY_DURATION, 1.0) * 200)
                    cv2.rectangle(frame, (20, self.height - 60), (20 + bar_width, self.height - 40), (0, 255, 255), -1)
                    cv2.rectangle(frame, (20, self.height - 60), (220, self.height - 40), (255, 255, 255), 2)
                    
                    if elapsed >= self.STABILITY_DURATION:
                        if center_name not in self.captured_map:
                            self.captured_map[center_name] = (current_names, current_bgr)
                            print(f"Captured: {center_name.capitalize()}")
                            print(f"Sticker colors for {center_name} face:")
                            for row in current_names:
                                print(f"  {row}")
                            self.stability_start_time = time.time() # Reset for next
                        elif center_name in self.captured_map:
                             cv2.putText(frame, "Already Captured", (20, self.height - 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                else:
                    self.stability_start_time = None
                    self.last_grid_names = None

                cv2.putText(frame, f"Captured: {len(self.captured_map)}/6", (self.width - 250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
            else:
                # Solving Phase
                cv2.putText(frame, "All Faces Captured! Processing...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # Short delay to show message
                cv2.imshow("Rubik's Solver", frame)
                cv2.waitKey(500) 
                break

            cv2.imshow("Rubik's Solver", frame)
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                self.cap.release()
                cv2.destroyAllWindows()
                return

        self.cap.release()
        cv2.destroyAllWindows()
        
        if len(self.captured_map) == 6:
            self.solve()

    def solve(self):
        print("\nConstructing Cube State...")
        
        # 1. Identify Center Colors (References)
        # We need the BGR values of the centers of the 6 captured faces
        # Map: color_name -> BGR_vector
        centers_bgr = {}
        for name, data in self.captured_map.items():
            _, grid_bgr = data
            centers_bgr[name] = grid_bgr[1][1] # Center piece

        # 2. Re-classify all 54 stickers based on nearest center color
        # We'll use CIELAB color space for better perceptual distance
        
        # Helper to convert single BGR to Lab
        def to_lab(bgr_pixel):
            # Reshape to 1x1x3 for cvtColor
            reshaped = np.uint8([[bgr_pixel]])
            lab = cv2.cvtColor(reshaped, cv2.COLOR_BGR2Lab)
            return lab[0][0].astype(int) # Return as int array

        # Convert centers to Lab
        centers_lab = {name: to_lab(bgr) for name, bgr in centers_bgr.items()}

        # Kociemba order: U (White), R (Red), F (Green), D (Yellow), L (Orange), B (Blue)
        solve_order = ['white', 'red', 'green', 'yellow', 'orange', 'blue']
        color_to_face = {
            'white': 'U',
            'red': 'R',
            'green': 'F',
            'yellow': 'D',
            'orange': 'L',
            'blue': 'B'
        }
        
        cube_string = ""
        
        print("Re-evaluating colors based on relative differences...")

        for face_color_name in solve_order:
            if face_color_name not in self.captured_map:
                print(f"Critical Error: Missing {face_color_name} face data.")
                return

            _, grid_bgr = self.captured_map[face_color_name]
            
            print(f"Final evaluated grid for {face_color_name} face:")
            for i in range(3):
                row_evaluated = []
                for j in range(3):
                    pixel_bgr = grid_bgr[i][j]
                    pixel_lab = to_lab(pixel_bgr)
                    
                    # Find closest center
                    min_dist = float('inf')
                    best_match = 'unknown'
                    
                    for center_name, center_lab in centers_lab.items():
                        # Euclidean distance in Lab space
                        dist = np.linalg.norm(pixel_lab - center_lab)
                        if dist < min_dist:
                            min_dist = dist
                            best_match = center_name
                    
                    cube_string += color_to_face[best_match]
                    row_evaluated.append(best_match)
                print(f"  {row_evaluated}")

        print(f"Refined Cube String: {cube_string}")
        
        try:
            print("Solving...")
            solution = kociemba.solve(cube_string)
            print(f"Solution Moves: {solution}")
            
            steps = self.format_solution(solution)
            print("\n--- Step-by-Step Instructions ---")
            for i, step in enumerate(steps):
                print(f"{i+1}. {step}")
                
        except Exception as e:
            print("\nError: Could not find a solution.")
            print("This usually means the colors were scanned incorrectly or the cube is physically unsolvable (sticker peeled?).")
            print(f"Details: {e}")

if __name__ == "__main__":
    solver = RubikSolver()
    solver.run()